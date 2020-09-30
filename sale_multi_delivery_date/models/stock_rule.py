# -*- coding: utf-8 -*-
from odoo import models, fields
class StockRule(models.Model):
	_inherit = 'stock.rule'

	# Pass the 'scheduled_date' in 'sale.order.line' to 'date_expected' in 'stock.move', this value will then be passed to 'scheduled_date' in 'stock.picking'
	def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
		res = super(StockRule,self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
		if values.get('sale_line_id'):
			line = self.env['sale.order.line'].browse(values.get('sale_line_id'))
			if line.scheduled_date:
				res.update({'date_expected':line.scheduled_date})
		return res