# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	@api.model_create_multi
	def create(self, vals_list):
		templates = super(ProductTemplate, self).create(vals_list)
		for template in templates:
			for variant in template.product_variant_ids:
				if variant.type == 'product':
					reordering_rule = {
						'product_min_qty': 0,
						'product_max_qty': 0,
						'product_id': variant.id
						}
					variant.update({'orderpoint_ids': [(0, 0, reordering_rule)]})

		return templates

	def write(self, vals):
		res = super(ProductTemplate, self).write(vals)
		if vals.get('type') == 'product':
			for template in self:
				if not template.nbr_reordering_rules:
					for variant in template.product_variant_ids:
						reordering_rule = {
							'product_min_qty': 0,
							'product_max_qty': 0,
							'product_id': variant.id
							}
						variant.update({'orderpoint_ids': [(0, 0, reordering_rule)]})
		
		return res



				
