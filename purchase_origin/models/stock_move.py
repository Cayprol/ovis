# -*- coding: utf-8 -*-
from odoo import fields, models

class StockMove(models.Model):
	_inherit = 'stock.move'

	po_generated = fields.Boolean('Purchase Order Generated', copy=False)