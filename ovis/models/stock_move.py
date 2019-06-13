# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class InheritStockMove(models.Model):

	_inherit = 'stock.move'

	net_weight = fields.Float('Net Weight', compute="_net_weight", digits=dp.get_precision('Stock Weight'), help="Net Weight of movement, calculated by the product weight per unit times quantity done.")
	gross_weight = fields.Float('Gross Weight', compute='_gross_weight_compute', digits=dp.get_precision('Stock Weight'), inverse='_gross_weight_set', help="Gross Weight of movement.")
	weight_uom = fields.Many2one('uom.uom', 'Weight Unit of Measure', required=True)

	@api.multi
	@api.depends('product_id', 'quantity_done')
	def _net_weight(self):
		for move in self:
			move.net_weight = move.product_id.weight * move.quantity_done


	@api.depends('move_line_ids.g_weight', 'move_line_ids.weight_uom_id', 'move_line_nosuggest_ids.g_weight')
	def _gross_weight_compute(self):
		for move in self:
			gross_weight = 0
			for move_line in move._get_move_lines():
				gross_weight += move_line.weight_uom_id._compute_quantity(move_line.g_weight, move.weight_uom, round=False)
			move.gross_weight = gross_weight

	# if not move_lines not applicable Error may happen
	def _gross_weight_set(self):
		gross_weight = self[0].gross_weight # any call to create will invalidate `move.gross_weight`
		for move in self:
			move_lines = move._get_move_lines()
			# if not move_lines:
			# 	if quantity_done:
			# 		# do not impact reservation here
			# 		move_line = self.env['stock.move.line'].create(dict(move._prepare_move_line_vals(), qty_done=quantity_done))
			# 		move.write({'move_line_ids': [(4, move_line.id)]})
			if len(move_lines) == 1:
				move_lines[0].g_weight = gross_weight
			else:
				raise UserError(_("Cannot set the done quantity from this stock move, work directly with the move lines."))

