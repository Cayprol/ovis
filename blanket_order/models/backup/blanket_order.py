# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
import json
import logging
_logger = logging.getLogger(__name__)
class BlanketOrder(models.Model):
	_name = 'blanket.order'
	_description = 'Blanket Orders'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_check_company_auto = True

	@api.model
	def _default_note_url(self):
		return self.env.company.get_base_url()

	@api.model
	def _default_note(self):
		use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
		if use_invoice_terms and self.env.company.terms_type == "html":
			baseurl = html_keep_url(self._default_note_url() + '/terms')
			return _('Terms & Conditions: %s', baseurl)
		return use_invoice_terms and self.env.company.invoice_terms or ''

	name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	state = fields.Selection([
		('draft', 'Draft'),
		('open', 'Open'),
		('closed', 'Closed'),
		('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
	date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of blanket orders,\nConfirmation date of open blanket orders.")

	sale_order_ids = fields.One2many('sale.order', 'blanket_order_id', string='Sale Orders', copy=False)
	purchase_order_ids = fields.One2many('purchase.order', 'blanket_order_id', string='Purchase Orders', copy=False)
	conversion_count = fields.Integer(string='Conversion Count', compute='_get_conversion')
	blanket_order_line = fields.One2many('blanket.order.line', 'blanket_order_id', string='Order Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
	order_type = fields.Selection([
		('sale', 'Sales'),
		('purchase', 'Purchase')], required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Blanket order for either customer or vendor.")
	workflow = fields.Selection([
		('pending', 'Pending'),
		('ready', 'Ready')], required=True, compute='_compute_workflow', help="Ready or not to close this order. User can safely ignore this field and manually close blanket orders.")

	partner_id = fields.Many2one(
		'res.partner', string='Customer', readonly=True,
		states={'draft': [('readonly', False)]},
		required=True, change_default=True, index=True, tracking=1,
		domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
	# partner_invoice_id = fields.Many2one(
	# 	'res.partner', string='Invoice Address',
	# 	readonly=True, required=True,
	# 	states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
	# 	domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
	partner_shipping_id = fields.Many2one(
		'res.partner', string='Delivery Address', readonly=True, required=True,
		states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
		domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
	pricelist_id = fields.Many2one(
		'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
		required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
		domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
		help="If you change the pricelist, only newly added lines will be affected.")
	currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=['pricelist_id'], store=True, ondelete='restrict')
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

	amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, compute='_amount_all', tracking=5)
	tax_totals_json = fields.Char(compute='_compute_tax_totals_json')
	amount_tax = fields.Monetary(string='Taxes', store=True, compute='_amount_all')
	amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all', tracking=4)

	note = fields.Html('Terms and conditions', default=_default_note)
	terms_type = fields.Selection(related='company_id.terms_type')

	@api.onchange('partner_id')
	def _onchange_partner_id_pricelist_id(self):
		self.pricelist_id = self._context.get('pricelist_id') or self.partner_id.property_product_pricelist

	@api.depends('blanket_order_line.price_total')
	def _amount_all(self):
		"""
		Compute the total amounts of the BO.
		"""
		for blanket_order in self:
			amount_untaxed = amount_tax = 0.0
			for line in blanket_order.blanket_order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			blanket_order.update({
				'amount_untaxed': amount_untaxed,
				'amount_tax': amount_tax,
				'amount_total': amount_untaxed + amount_tax,
			})

	@api.depends('blanket_order_line.tax_id', 'blanket_order_line.price_unit', 'amount_total', 'amount_untaxed')
	def _compute_tax_totals_json(self):
		def compute_taxes(blanket_order_line):
			price = blanket_order_line.price_unit * (1 - (blanket_order_line.discount or 0.0) / 100.0)
			blanket_order = blanket_order_line.blanket_order_id
			return blanket_order_line.tax_id._origin.compute_all(price, blanket_order.currency_id, blanket_order_line.product_uom_qty, product=blanket_order_line.product_id, partner=blanket_order.partner_shipping_id)

		account_move = self.env['account.move']
		for blanket_order in self:
			tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(blanket_order.blanket_order_line, compute_taxes)
			tax_totals = account_move._get_tax_totals(blanket_order.partner_id, tax_lines_data, blanket_order.amount_total, blanket_order.amount_untaxed, blanket_order.currency_id)
			blanket_order.tax_totals_json = json.dumps(tax_totals)
	
	@api.depends('blanket_order_line.qty_converted')
	def _get_conversion(self):
		for order in self:
			ids = {'sale': order.sale_order_ids, 'purchase': order.purchase_order_ids}
			order.conversion_count = len(ids.get(order.order_type, 0))

	@api.depends('blanket_order_line.product_uom_qty')
	def _compute_workflow(self):
		for order in self:
			order.workflow = 'ready' if order.blanket_order_line and all(qty == 0 for qty in order.blanket_order_line.mapped('product_uom_qty')) else 'pending'

	@api.model
	def create(self, vals):
		if 'company_id' in vals:
			self = self.with_company(vals['company_id'])
		if vals.get('name', _('New')) == _('New'):
			seq_date = None
			if 'date_order' in vals:
				seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
			vals['name'] = self.env['ir.sequence'].next_by_code('blanket.order', sequence_date=seq_date) or _('New')

		return super(BlanketOrder, self).create(vals)

	def action_open(self):
		draft = self.filtered(lambda order: order.state == 'draft')
		remaining = self-draft
		# raise Error if selected recordset contains states other than draft
		if remaining:
			raise exceptions.UserError(_('Only Order Status in Draft are allowed to be opened.'))

		draft.write({'state': 'open'})

	def action_close(self):
		open_orders = self.filtered(lambda order: order.state == 'open')
		remaining = self-open_orders
		# raise Error if selected recordset contains states other than open
		if remaining:
			raise exceptions.UserError(_('Only Order Status in Open are allowed to be closed.'))

		open_orders.write({'state': 'closed'})

	def action_convert(self):
		self.ensure_one()
		if self.state != 'open':
			raise exceptions.UserError(_('Only Order Status in Open are allowed to be converted.'))

		order_lines = []
		for line in self.blanket_order_line:
			order_lines.append((0, False, {
					'product_id': line.product_id.id,
					'name': line.name,
					'product_uom_qty': line.qty_to_convert,
					'product_uom': line.product_uom.id,
					'price_unit': line.price_unit,
					# Taxes
					'discount': line.discount,
					'display_type': line.display_type,}))
			line.product_uom_qty -= line.qty_to_convert
			line.qty_converted += line.qty_to_convert
			line.qty_to_convert = 0

		default_ctx = {
			'default_partner_id': self.partner_id.id,
			'default_pricelist_id': self.pricelist_id.id,
			'default_order_line': order_lines,
			'default_blanket_order_id': self.id,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'sale.order',
			'views': [(self.env.ref('sale.view_order_form').id, 'form')],
			'view_id': self.env.ref('sale.view_order_form').id,
			'target': 'new', # default is current
			'context': default_ctx
		}


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	blanket_order_id = fields.Many2one('blanket.order', string='Blanket Order Reference', ondelete='restrict', index=True, copy=False)

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	blanket_order_id = fields.Many2one('blanket.order', string='Blanket Order Reference', ondelete='restrict', index=True, copy=False)