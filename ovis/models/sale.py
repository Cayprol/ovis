# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.misc import formatLang

class InheritSaleOrder(models.Model):

	_inherit = 'sale.order'

	ask_approve_date = fields.Date('Ask Approval Date', readonly=1, index=True, copy=False)
	approve_date = fields.Date('Approval Date', readonly=1, index=True, copy=False)
	approver_id = fields.Many2one('res.users', 'Quotation Approver', readonly=True, copy=False, track_visibility='onchange')

	quotation_id = fields.Many2one('sale.order', 'Quotation Reference', readonly=True, states={'draft': [('readonly', False)]}, copy=False, track_visibility='onchange', domain="[('state', '=', 'sent')]")

	state = fields.Selection([('draft', 'Quotation'),
							 ('to approve', 'To Approve'),
							 ('sent', 'Quotation Sent'),
							 ('sale', 'Sales Order'),
							 ('done', 'Locked'),
							 ('cancel', 'Cancelled'),],
							 string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

	@api.multi
	def action_ask_approve(self, force=False):
		self.write({'state': 'to approve', 'ask_approve_date': fields.Date.context_today(self)})
		return {}
		
	@api.multi
	def action_approve(self, force=False):
		self.write({'state': 'sent', 'approve_date': fields.Date.context_today(self)})
		self.approver_id = self.env.user
		return {}


	# change quotation_id domain dynamically based on partner_id selected
	@api.onchange('partner_id')
	def onchange_quotation_id_domain(self):
		domain = [('state', '=', 'sent')]
		if self.partner_id:
			domain += [('partner_id', 'child_of', self.partner_id.id)]

		return {'domain':{'quotation_id': domain}}


	# method called in onchange_fill_order_line for storing existing 'order_line' in a dictionary
	def _prepare_new_order_line_from_order_line(self, line):
		data ={
			'product_id': line.product_id,
			'name': line.name,
			'product_uom_qty': line.product_uom_qty,
			'qty_delivered': line.qty_delivered,
			'qty_invoiced': line.qty_invoiced,
			'product_uom': line.product_uom,
			'price_unit': line.price_unit,
			'purchase_price': line.purchase_price,
			'tax_id': line.tax_id,
			'price_total': line.price_total,
		}

		return data

	# generate new order_line from another 'sale.order' record which does not affect what it's been generated from
	@api.onchange('quotation_id')
	def onchange_fill_order_line(self):
		new_lines = self.env['sale.order.line']
		for line in self.quotation_id.order_line:
			data = self._prepare_new_order_line_from_order_line(line)
			new_line = new_lines.new(data)
			# new_line._set_additional_fields(self)
			new_lines += new_line

		self.order_line += new_lines
		self.payment_term_id = self.quotation_id.payment_term_id    # Load payment_term_id as well
		# self.env.context = dict(self.env.context, from_purchase_order_change=True)
		self.quotation_id = False     # Only load order_line, deselect Quotation number
		return {}


	# generate new name, based on context 'show_total_amount' from xml view
	@api.multi
	@api.depends('name', 'client_order_ref')
	def name_get(self):
		result = []
		for qo in self:
			name = qo.name
			if qo.client_order_ref:
				name += ' (' + qo.client_order_ref + ')'
			if self.env.context.get('show_total_amount') and qo.amount_total:
				name += ': ' + formatLang(self.env, qo.amount_total, currency_obj=qo.currency_id)
			result.append((qo.id, name))
		return result

	# Disable buttons 'Send Email' and 'Send Pro-forma Invoice' to move 'sale.order' to 'state': 'sent'
	@api.multi
	def action_quotation_send(self):
		parent_result = super().action_quotation_send()
		parent_result['context']['mark_so_as_sent'] = False

		return dict1

	# Disable buttons 'Print' to move 'sale.order' to 'state': 'sent'
	@api.multi
	def print_quotation(self):
		return self.env.ref('sale.action_report_saleorder')\
			.with_context({'discard_logo_check': True}).report_action(self)