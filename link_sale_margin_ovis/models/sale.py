# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	def _prepare_order_line(self, order_line, option=False):
		res = super(SaleOrder, self)._prepare_order_line(order_line, option)

		for r, line in zip(res, order_line):
			r[2]['purchase_price'] = line.purchase_price

		return res