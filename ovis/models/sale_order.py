# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# This field is created because the <create> tag cannot be hide conditionally by state through the 'attrs' attribute
	order_line_confirmed = fields.One2many('sale.order.line', 'order_id', string='Order lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

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

					'product_id': line.product_id.id,
					'name': line.name,
					# scheduled_date # 'scheduled_date': line.scheduled_date, # link module 'link_ovis_sale_multi_delivery_date' pass this value
					'route_id': line.route_id.id,
					'product_uom_qty': line.product_uom_qty,
					'product_uom': line.product_uom.id,
					'customer_lead': line.customer_lead,
					'price_unit': line.price_unit,
					# purchase_price # 'purchase_price': line.purchase_price, # link module 'link_ovis_sale_margin' pass this value
					# margin # 'purchase_price': line.purchase_price, # link module 'link_ovis_sale_margin' pass this value
					# margin_percent # 'purchase_price': line.purchase_price, # link module 'link_ovis_sale_margin' pass this value
					# Taxes
					# 'discount': line.discount,
					'display_type': line.display_type,
					'is_downpayment': line.is_downpayment,
					'is_expense': line.is_expense,
						}
					) for line in order_line ]

		return order_lines

	def _action_send(self):
		self.write({'state': 'sent'})
		return  {'type': 'ir.actions.client', 'tag': 'reload'}


	def action_send(self):
		not_draft_orders = self.filtered(lambda order: order.state != 'draft')
		if not_draft_orders:
			raise exceptions.UserError(_("Only draft Quotation are allowed to be sent.\nFollowing documents are not in draft.\n{docs}".format(docs=not_draft_orders.name)))
		else:
			return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'confirm.popup',
				'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
				'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
				'target': 'new',
				'res_id': self.env['confirm.popup'].create({}).id,
				'name': _('Prepare this quotation to be sent?'),
				'context': {
					'run_action': '_action_send',
					'model': self._name,
					'res_id': self.ids,
					},
				}

	# Rely on module 'confirm.popup', call popup wizard as warning & user input log before cancelling
	def action_cancel_2step(self):
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'name': _('Would you like to cancel?'),
			'context': {
				'run_action': 'action_cancel',
				'model': self._name,
				'res_id': self.ids,
				},
			}

	def action_create_sales_order(self):
		self.ensure_one()
		default_ctx = {
			'default_partner_id': self.partner_id.id, 
			'default_partner_invoice_id': self.partner_invoice_id.id,
			'default_partner_shipping_id': self.partner_shipping_id.id,
			'default_validity_date': self.validity_date,
			'default_date_order': self.date_order,
			'default_pricelist_id': self.pricelist_id.id,
			'default_payment_term_id': self.payment_term_id.id, # Due to on_change method, passing defualt_value in context doens't work. Still passing it for the overriden on_change method below.
			'default_user_id': self.user_id.id,
			'default_team_id': self.team_id.id,
			'default_require_signature': self.require_signature,
			'default_require_payment': self.require_payment,
			'default_client_order_ref': self.client_order_ref,
			# Tags
			'default_fiscal_position_id': self.fiscal_position_id.id,
			'default_incoterm': self.incoterm.id,
			'default_picking_policy': self.picking_policy,
			'default_commitment_date': self.commitment_date,
			'default_origin': self.name,
			'default_campaign_id': self.campaign_id.id,
			'default_medium_id': self.medium_id.id,
			'default_source_id': self.source_id.id,
			'default_currency_id': self.currency_id.id,
			'default_order_line': self._prepare_order_line(self.order_line),
			# 'default_sale_order_option_ids': self._prepare_order_line(self.sale_order_option_ids, option=True),
			'create_sales_order': True,
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'sale.order',
			'views': [(self.env.ref('sale.view_order_form').id, 'form')],
			'view_id': self.env.ref('sale.view_order_form').id,
			# 'target': 'current', # default is current
			'context': default_ctx
		}

	def action_confirm(self):
		super(SaleOrder, self).action_confirm()
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'sale.order',
			'views': [(False, 'form')],
			'res_id': self.ids[0], # res_id is a must, otherwise a new record is created
			# 'target': 'main', # main/current makes no difference
			'context': {
				# 'form_view_initial_mode': 'browse',
				'no_breadcrumbs': True,
			},
		}

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		super(SaleOrder, self).onchange_partner_id()
		partner_invoice_id = self._context.get('default_partner_invoice_id', False)
		partner_shipping_id = self._context.get('default_partner_shipping_id', False)
		payment_term_id = self._context.get('default_payment_term_id', False)
		if partner_invoice_id:
			self.update({'partner_invoice_id': partner_invoice_id})
		if partner_shipping_id:
			self.update({'partner_shipping_id': partner_shipping_id})
		if payment_term_id:
			self.update({'payment_term_id': payment_term_id})

	@api.onchange('partner_shipping_id', 'partner_id', 'company_id')
	def onchange_partner_shipping_id(self):
		res = super(SaleOrder, self).onchange_partner_shipping_id()
		fiscal_position_id = self._context.get('default_fiscal_position_id')
		if fiscal_position_id:
			self.update({'fiscal_position_id': fiscal_position_id})

		return res