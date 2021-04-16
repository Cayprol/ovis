# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _ 
import logging
_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

	_inherit = 'sale.order'

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('quotation') or _('New')
		return super(SaleOrder, self).create(vals)

	def action_test(self):
		return {'type': 'ir.actions.client',
				'tag': 'reload_view'}

	def action_confirm(self):
		if self._get_forbidden_state_confirm() & set(self.mapped('state')):
			raise UserError(_(
				'It is not allowed to confirm an order in the following states: %s'
			) % (', '.join(self._get_forbidden_state_confirm())))

		for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
			order.message_subscribe([order.partner_id.id])
		self.write({
			'name': self.env['ir.sequence'].next_by_code('sale.order'),
			'state': 'sale',
			'date_order': fields.Datetime.now()
		})

		# Context key 'default_name' is sometimes propagated up to here.
		# We don't need it and it creates issues in the creation of linked records.
		context = self._context.copy()
		context.pop('default_name', None)

		self.with_context(context)._action_confirm()
		if self.env.user.has_group('sale.group_auto_done_setting'):
			self.action_done()

		return {
			'type': 'ir.actions.act_multi',
			'actions': [{
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'res_model': 'sale.order',
				'views': [(self.env.ref('sale.view_order_form').id, 'form')],
				'res_id': self.id,
				'target': 'main', # new, inline, main, current, fullscreen
				'context': {'form_view_initial_mode': 'view'} # 'force_detailed_view': True # Not sure what this do
				},
				{'type': 'ir.actions.client', 'tag': 'reload'},
			],
		}

	# Rely on module 'confirm.popup', call popup wizard as warning & user input log before cancelling
	def action_cancel_2step(self):
		return {
			'name': _('Would you like to cancel?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.ids,
						'method': 'action_cancel',
						'log_title': _("Cancelling Reason:"),
						},
			}

	# Odoo standard workflow 'draft' to 'sent' got too many buttons for doing it.
	# This action simply move the state
	# Rely on module 'confirm.popup', call popup wizard as warning & optional user input for logging
	def action_send(self):
		for order in self:
			if order.state != 'draft':
				raise exceptions.UserError(_("Only unsent Quotation are allowed to be sent."))

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
						'parent_id': self.ids,
						'method': 'write',
						'method_args': [{'state': 'sent'}],
						'log_title': "Send Memo:",
						},
			}

	# Creates a pseudo-record with default values taken from current form view which 'state' is 'sent'
	def action_create_sales_order(self):
		self.ensure_one()
		default_ctx = {
			'default_client_order_ref': self.client_order_ref,
			'default_commitment_date': self.commitment_date,
			'default_validity_date': self.validity_date,
			'default_currency_id': self.currency_id.id,
			'default_date_order': self.date_order,
			'default_partner_id': self.partner_id.id, 
			'default_order_line': self._prepare_order_line(self.order_line),
			'default_sale_order_option_ids': self._prepare_order_line(self.sale_order_option_ids, option=True),
			'default_picking_policy': self.picking_policy,
			'default_pricelist_id': self.pricelist_id.id,
			'default_warehouse_id': self.warehouse_id.id,
			'default_fiscal_position_id': self.fiscal_position_id.id,
			'default_incoterm': self.incoterm.id,
			'default_require_signature': self.require_signature,
			'default_require_payment': self.require_payment,
			# 'default_state': self.state, # This will break following procuremnt stock.move has a field state and in context default_state='sent' will be interfered.
			'convert_lock': False,
			'default_origin': self.name,
			'default_payment_term_id': self.payment_term_id.id # Due to on_change method, passing defualt_value in context doens't work. Still passing it for the overriden on_change method below.
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'sale.order',
			'views': [(self.env.ref('sale.view_order_form').id, 'form')],
			'view_id': self.env.ref('sale.view_order_form').id,
			'target': 'current',
			# 'target': 'inline',
			'context': default_ctx
		}

	# Work with action_create_sales_order() which reads exisiting One2many and make them re-creatable
	def _prepare_order_line(self, order_line, option=False):
		if option:
			order_lines = [
				(0, False, {
					'order_id': self.id,
					'discount': line.discount,
					'name': line.name,
					'price_unit': line.price_unit,
					'product_id': line.product_id.id,
					'uom_id': line.uom_id.id,
					'quantity': line.quantity,
						}
					) for line in order_line ]
		else:
			order_lines = [
				(0, False, {
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
					'scheduled_date': line.scheduled_date,
						}
					) for line in order_line ]

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
		for line in self.order_line:
			line.update({'tally': False})
		return super(SaleOrder, self).action_draft()

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		res = {}
		super(SaleOrder, self).onchange_partner_id()
		if not self._context.get('convert_lock') and self._context.get('default_payment_term_id'):
			res = {'payment_term_id': self._context.get('default_payment_term_id')}
		self.update(res)



	tally = fields.Boolean('Tally', compute="_compute_tally", store=True, readonly=True, help="This field indicates all order lines associated to this order are notified for tally or not.")

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	tally = fields.Boolean('Tally', help="This field indicates the order line has been notified for tally or not.")