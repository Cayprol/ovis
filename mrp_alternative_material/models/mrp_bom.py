# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MrpBomLine(models.Model):
	_inherit = 'mrp.bom.line'

	alternative_product_ids = fields.Many2many('product.product', string='Alternatives')
