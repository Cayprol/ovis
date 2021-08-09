# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Product(models.Model):
	_inherit = 'product.product'

	def at_least_1_reordering_rule_per_company(self):
		sudo_company_ids = self.env['res.company'].sudo().search([])
		for variant_id in self.env['product.product'].sudo().search([('type', '=', 'product')]):
			orderpoint_ids = self.env['stock.warehouse.orderpoint'].sudo().search([('product_id', '=', variant_id.id)])
			company_ids = sudo_company_ids - orderpoint_ids.company_id
			if company_ids:
				_logger.warning("new company_ids {}, type {}".format(company_ids, type(company_ids)))
				reordering_rules = [{
					'company_id': company_id.id,
					'product_id': variant_id.id,
					'product_max_qty': 0,
					'product_min_qty': 0,
					'warehouse_id': self.env['stock.warehouse'].sudo().search([('company_id', '=', company_id.id)])[0].id,
					'location_id': self.env['stock.warehouse'].sudo().search([('company_id', '=', company_id.id)])[0].lot_stock_id.id,
					} for company_id in company_ids]
				_logger.warning(reordering_rules)
				self.env['stock.warehouse.orderpoint'].create(reordering_rules)