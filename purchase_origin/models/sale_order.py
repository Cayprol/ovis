# -*- coding: utf-8 -*-
# Override module 'sale_stock'
from odoo import fields, models

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	"""
	Only 'store=True' can be .search()
	These 2 fieds share the same compute method,
	If not both 'stored=True', a warning of 
	"inconsistent 'compute_sudo' for computed fields: " will be raised
	"""
	qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver', store=True)
	display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver', store=True)
