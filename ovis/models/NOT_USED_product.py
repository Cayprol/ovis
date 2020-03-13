# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductProduct(models.Model):

	_inherit = 'product.product'

	drawing = fields.Char('Drawing', copy=False, help="Engineering Drawing for particular product.")
