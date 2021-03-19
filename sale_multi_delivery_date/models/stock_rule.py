# -*- coding: utf-8 -*-
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class StockRule(models.Model):
	_inherit = 'stock.rule'
	
	# Pass 'sale.order.line', field 'scheduled_date' to 'stock.move', 'date_expected'
	# _get_stock_move_values(), in res, both'date' and 'date_expected' are assigned with variable date_expected, hence both are updated in this overriden method.
	def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
		res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
		_logger.info("values in stock_rule is {}".format(values))
		if values.get('sale_line_id'):
			line = self.env['sale.order.line'].browse(values.get('sale_line_id'))
			if line.scheduled_date:
				res.update({'date':line.scheduled_date,
							'date_expected':line.scheduled_date})
		return res