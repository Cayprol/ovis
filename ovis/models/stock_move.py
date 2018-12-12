# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class InheritStockMove(models.Model):

	_inherit = 'stock.move'

	net_weight = fields.Float('Net Weight', compute="_net_weight", digits=dp.get_precision('Stock Weight'), help="Net Weight of movement, calculated by the product weight per unit times quantity done.")
	gross_weight = fields.Float('Gross Weight', digits=dp.get_precision('Stock Weight'), help="Gross Weight of movement.")

	@api.multi
	@api.depends('product_id', 'quantity_done')
	def _net_weight(self):
		for move in self:
			move.net_weight = move.product_id.weight * move.quantity_done



