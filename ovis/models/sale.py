# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

	_inherit = 'sale.order'

	# Quotation in 'draft' and 'sent' have different name sequence
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('quotation') or _('New')
		return super(SaleOrder, self).create(vals)

	# When action_confirm(), a write() with args of state='sale' is passed. Rename quotation name
	def write(self, values):
		if values.get('state') == 'sale':
			values['name'] = self.env['ir.sequence'].next_by_code('sale.order')
		return super(SaleOrder, self).write(values)

	# Rely on module 'confirm.popup', call popup wizard as warning & user input log before cancelling
	def action_cancel(self):
		self.ensure_one()
		return {
			'name': _('Cancel this record?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,
						'method': 'update',
						'method_params': {'state': 'cancel'},
						'log_title': "Cancelling Reason:",
						},
			}

	# Odoo standard workflow 'draft' to 'sent' got too many buttons for doing it.
	# This action simply move the state
	# Rely on module 'confirm.popup', call popup wizard as warning & optional user input for logging
	def action_send(self):
		self.ensure_one()
		if self.state != 'draft':
			raise exceptions.ValidationError(_("Only draft state are allowed to be sent."))

		return {
			'name': _('Prepare this quotation to be sent?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,
						'method': 'update',
						'method_params': {'state': 'sent'},
						'log_title': "Send Memo:",
						},
			}

	# Creates a pseudo-record with default values taken from current form view which 'state' is 'sent'
	def action_link(self):
		self.ensure_one()
		default_ctx = {
			'default_client_order_ref': self.client_order_ref,
			'default_commitment_date': self.commitment_date,
			'default_validity_date': self.validity_date,
			'default_currency_id': self.currency_id.id,
			'default_date_order': self.date_order,
			'default_partner_id': self.partner_id.id, 
			'default_order_line': self._prepare_order_line(),
			'default_picking_policy': self.picking_policy,
			'default_pricelist_id': self.pricelist_id.id,
			'default_warehouse_id': self.warehouse_id.id,
			'default_fiscal_position_id': self.fiscal_position_id.id,
			'default_incoterm': self.incoterm.id,
			'default_require_signature': self.require_signature,
			'default_require_payment': self.require_payment,
			# 'default_state': self.state, # This will break following procuremnt stock.move has a field state and in context default_state='sent' will be interfere.
			'convert_lock': False,
			'default_origin': self.name,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'sale.order',
			'views': [(self.env.ref('sale.view_order_form').id, 'form')],
			'view_id': self.env.ref('sale.view_order_form').id,
			'target': 'current',
			'context': default_ctx
		}

	# Work with action_link() which reads exisiting One2many and make them re-creatable
	def _prepare_order_line(self):
		order_lines = []
		for line in self.order_line:
			order_lines.append((0, False, {
				'order_id': self.id,
				'customer_lead': line.customer_lead,
				'discount': line.discount,
				'display_type': line.display_type,
				'is_downpayment': line.is_downpayment,
				'is_expense': line.is_expense,
				'name': line.name,
				'order_partner_id': line.order_partner_id.id,
				'price_unit': line.price_unit,
				'product_id': line.product_id.id,
				'product_uom': line.product_uom.id,
				'product_uom_qty': line.product_uom_qty,
				}))

		return order_lines

	@api.depends('order_line.tally')
	def _compute_tally(self):
		for order in self:
			if order.state in ['draft', 'sent']:
				res = {'tally': False}
			else:
				notified = [line.tally for line in order.order_line]
				res = {'tally': all(notified)}

			order.update(res)

	def action_draft(self):
		super(SaleOrder, self).action_draft()
		for line in self.order_line:
			line.update({'tally': False,
						# 'sale_delivery_date': fields.date.today(),
						})
		return True

	# @api.onchange('partner_id')
	# def onchange_domain_partner_invoice_id(self):
	# 	if self.partner_id:
	# 		res = {'domain': {'partner_invoice_id': [('parent_id.id', '=', self.partner_id.id)]}}
	# 		return res
	# 	else:
	# 		return False

	# def write(self, values):
	# 	if values.get('order_line') and self.state == 'sale':

	# 		_logger.info(values['order_line'])

	# 		for order in self:
	# 			to_log={}
	# 			for value in values['order_line']:
	# 				if value[1] is int:
	# 					line = order.order_line.browse(value[1])
	# 					if type(value[2]) == dict:
	# 						if value[2].get('sale_delivery_date'):
	# 							if line.sale_delivery_date != value[2]['sale_delivery_date']:
	# 								_logger.info("Date Changed.")
	# 								to_log[line] = (line.sale_delivery_date, value[2]['sale_delivery_date'])
	# 			if to_log:
	# 				documents = self.env['stock.picking']._log_activity_get_documents(to_log, 'move_ids', 'UP')
	# 				order._log_change_delivery_date(documents)

	# 	return super(SaleOrder, self).write(values)

	# def _log_change_delivery_date(self, documents, cancel=False):
	# 	def _render_note_exception_delivery_so(rendering_context):
	# 		order_exceptions, visited_moves = rendering_context
	# 		visited_moves = list(visited_moves)
	# 		visited_moves = self.env[visited_moves[0]._name].concat(*visited_moves)
	# 		order_line_ids = self.env['sale.order.line'].browse([order_line.id for order in order_exceptions.values() for order_line in order[0]])
	# 		sale_order_ids = order_line_ids.mapped('order_id')
	# 		impacted_pickings = visited_moves.filtered(lambda m: m.state not in ('done', 'cancel')).mapped('picking_id')
	# 		values = {
	# 			'sale_order_ids': sale_order_ids,
	# 			'order_exceptions': order_exceptions.values(),
	# 			'impacted_pickings': impacted_pickings,
	# 			'cancel': cancel
	# 		}
	# 		return self.env.ref('ovis.exception_on_so').render(values=values)
	# 	self.env['stock.picking']._log_activity(_render_note_exception_delivery_so, documents)

	tally = fields.Boolean('Tally', compute="_compute_tally", store=True, readonly=True, help="This field indicates all order lines associated to this order are notified for tally or not.")

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	tally = fields.Boolean('Tally', help="This field indicates the order line has been notified for tally or not.")

	# @api.onchange('sale_delivery_date')
	# def _onchange_sale_delivery_date(self):
	# 	if self.state in ['sale']: 
	# 		return {
	# 			'warning': {
	# 				'title': _('Delivery Order has been scheduled.'),
	# 				'message': _("Please, double check the scheduled date of all corresponding delivery orders.")
	# 			}
	# 		}