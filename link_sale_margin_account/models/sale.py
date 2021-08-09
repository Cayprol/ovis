# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	def _prepare_invoice_line(self):
		res = super(SaleOrderLine, self)._prepare_invoice_line()
		res.update({'purchase_price': self.purchase_price})
		return res