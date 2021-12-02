# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

class SaleOrder(models.Model):
	_inherit = 'sale.order'
	"""
	Field 'purchase_price' provided by standard Odoo module 'sale_margin'.
	This method is overriden to pass 'purchase_price' from SOL to work with custom quotation-to-sale-order flow.
	"""
	def _prepare_order_line(self, order_line, option=False):
		pseudo_order_lines = super(SaleOrder, self)._prepare_order_line(order_line)
		if not option:
			for line, o2m_line in zip(order_line, pseudo_order_lines):
				o2m_line[2].update({'purchase_price': line.purchase_price})
		return pseudo_order_lines

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	"""
	'purchase_price' is a editable computed field.
	Override it to NOT compute, if the sale order is being set from 'sent' to 'pseudo-draft'.
	"""
	@api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
	def _compute_purchase_price(self):
		if self._context.get('create_sales_order'):
			for line in self:
				continue
		else:
			super(SaleOrderLine, self)._compute_purchase_price()