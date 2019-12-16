# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

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

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	@api.depends('product_uom_qty', 'qty_delivered', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		super(SaleOrder, self)._compute_amount()
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




