# -*- coding: utf-8 -*-
from odoo import models, fields

class StockRule(models.Model):
	_inherit = 'stock.rule'
	
	# _get_stock_move_values is defined in module 'stock/models/sotck_rule.py'
	# Pass 'sale.order.line', field 'scheduled_date' to 'stock.move', 'date_deadline'
	# _get_stock_move_values(), in res, both 'date' and 'date_deadline' are assigned with variable date_deadline, hence both are updated in this overriden method.
	def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
		res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
		if values.get('sale_line_id'):
			line = self.env['sale.order.line'].browse(values.get('sale_line_id'))
			if line.scheduled_date:
				res.update({'date':line.scheduled_date,
							'date_deadline':line.scheduled_date})
		return res