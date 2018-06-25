# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritProductTemplate(models.Model):

	_inherit = 'sale.order'

	# external_ref = fields.Char(string='External Reference', index=True, help="Source or Reference for this Sale Order.  eg, Customer P/O number / Email archive")

