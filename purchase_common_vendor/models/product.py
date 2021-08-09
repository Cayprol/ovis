# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SupplierInfo(models.Model):
	_inherit = "product.supplierinfo"

	company_id = fields.Many2one('res.company', 'Company', default=None, index=1)
