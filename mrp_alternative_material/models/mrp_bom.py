# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MrpBomLine(models.Model):
	_inherit = 'mrp.bom.line'

	alternative_product_ids = fields.Many2many(
		'product.product',
		'bom_line_product_variant_rel',
		'bom_line_id',
		'product_variant_id',
		string='Alternatives')

	code = fields.Char(related='bom_id.code')
