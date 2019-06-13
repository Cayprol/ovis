# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class InheritStockMoveLine(models.Model):
	
	_inherit = 'stock.move.line'

	g_weight = fields.Float('Gross Weight', default=0.0, digits=dp.get_precision('Stock Weight'), copy=False, help="Gross Weight of movement.")

	weight_uom_id = fields.Many2one(related="product_id.weight_uom_id", string="Weight Unit of Measure", readonly=True)

	# @api.constrains('g_weight')
	# def _check_positive_g_weight(self):
	# 	if any([ml.g_weight < 0 for ml in self]):
	# 		raise ValidationError(_('You can not enter negative weight.'))