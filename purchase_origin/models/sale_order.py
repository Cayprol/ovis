# -*- coding: utf-8 -*-
# Override module 'sale_stock'
from odoo import fields, models

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	"""
	Computed fields must be 'store=True' in order to .search()
	These 2 fields share the same compute method,
	If not both 'stored=True', a warning of 
	"inconsistent 'compute_sudo' for computed fields: " will be raised
	"""
	qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver', store=True)
	display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver', store=True)

	po_generated = fields.Boolean('Purchase Order Generated', copy=False)
