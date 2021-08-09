# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	"""
	Override create method to work with multi-create
	Create reordering rules for all companies the user is currently signed in.
	"""
	@api.model_create_multi
	def create(self, vals_list):
		templates = super(ProductTemplate, self).create(vals_list)
		company_ids = self.env['res.company'].sudo().search([])
		for template in templates:
			for variant in template.product_variant_ids:
				if variant.type == 'product':
					for company_id in company_ids:
						warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id', '=', company_id.id)])

						# Company might have multiple warehouses, choose the first one found.
						_logger.warning("warehouse_ids {}, type {}".format(warehouse_ids, type(warehouse_ids)))
						warehouse_id = warehouse_ids[0]
						# _logger.warning('company {} warehouses found {}, warehouse select {}, type ids {}, type id {}'.format(company_id, warehouse_ids, warehouse_id, type(warehouse_ids), type(warehouse_id)))
						reordering_rule = {
							'product_min_qty': 0,
							'product_max_qty': 0,
							'product_id': variant.id,
							'company_id': company_id.id,
							'warehouse_id': warehouse_id.id,
							'location_id': warehouse_id.lot_stock_id.id,
							}
						variant.sudo().update({'orderpoint_ids': [(0, 0, reordering_rule)]})

		return templates