# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

	_inherit = 'sale.order'

	@api.depends('order_line.price_total')
	def _amount_all(self):
		super(SaleOrder, self)._amount_all()

		for order in self:
			backed_amount_untaxed = backed_amount_tax = 0.0
			for line in order.order_line:
				backed_amount_untaxed += line.backed_price_subtotal
				backed_amount_tax += line.backed_price_tax
			order.update({
				'backed_amount_untaxed': backed_amount_untaxed,
				'backed_amount_tax': backed_amount_tax,
				'backed_amount_total': backed_amount_untaxed + backed_amount_tax,
			})

	backed_amount_untaxed = fields.Monetary(string='Backorder Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=5)
	backed_amount_tax = fields.Monetary(string='Backorder Taxes', store=True, readonly=True, compute='_amount_all')
	backed_amount_total = fields.Monetary(string='Backorder Total', store=True, readonly=True, compute='_amount_all', tracking=4)

	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		if toolbar:
			actions_in_toolbar = res['toolbar'].get('action')
			if actions_in_toolbar:
				for action in actions_in_toolbar:
					if action.get('xml_id'):
						if action['xml_id'] == 'sale.model_sale_order_action_quotation_sent' and self._context.get('act_window_id') == 'sale_back_order.action_back_orders':
							res['toolbar']['action'].remove(action)
						if action['xml_id'] == 'sale_back_order.action_backorder_line' and not self._context.get('act_window_id') == 'sale_back_order.action_backorder_line':
							res['toolbar']['action'].remove(action)

		return res

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	@api.depends('product_uom_qty', 'qty_delivered', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		super(SaleOrderLine, self)._compute_amount()
		for line in self:
			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			qty_backed = line.product_uom_qty - line.qty_delivered
			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, qty_backed, product=line.product_id, partner=line.order_id.partner_shipping_id)
			line.update({
				'backed_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
				'backed_price_total': taxes['total_included'],
				'backed_price_subtotal': taxes['total_excluded'],
			})

	backed_price_tax = fields.Float(compute='_compute_amount', string='Backed Total Tax', readonly=True, store=True)
	backed_price_total = fields.Monetary(compute='_compute_amount', string='Backed Total', readonly=True, store=True)
	backed_price_subtotal = fields.Monetary(compute='_compute_amount', string='Backed Subtotal', readonly=True, store=True)

	client_order_ref = fields.Char(related="order_id.client_order_ref")

	partner_shipping_id = fields.Many2one(related="order_id.partner_shipping_id", store=True, readonly=True)


