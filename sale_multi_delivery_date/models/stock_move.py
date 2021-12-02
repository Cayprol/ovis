# -*- coding: utf-8 -*-
from odoo import models, fields
from itertools import groupby


class StockMove(models.Model):
	_inherit = 'stock.move'	
	
	# _get_new_picking_values is defined in module 'stock/models/stock_move.py'
	# assign move 'scheduled_date' to picking delivery date
	def _get_new_picking_values(self):
		res = super(StockMove, self)._get_new_picking_values()
		res.update({'scheduled_date': self.sale_line_id.scheduled_date})
		return res

	# _search_picking_for_assignation is defined in module 'stock/models/stock_move.py'
	# Search Picking for move and assign to picking to move 
	def _search_picking_for_assignation(self):
		res = super(StockMove, self)._search_picking_for_assignation()
		if self.date_deadline:
			picking = self.env['stock.picking'].search([
				('group_id', '=', self.group_id.id),
				('location_id', '=', self.location_id.id),
				('location_dest_id', '=', self.location_dest_id.id),
				('picking_type_id', '=', self.picking_type_id.id),
				('scheduled_date','=', self.date_deadline),
				('printed', '=', False),
				('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
			return picking
		return res

	# _assign_picking is defined in module 'stock/models/stock_move.py'
	def _assign_picking(self):
		""" Try to assign the moves to an existing picking that has not been
		reserved yet and has the same procurement group, locations and picking
		type (moves should already have them identical). Otherwise, create a new
		picking to assign them to. """
		Picking = self.env['stock.picking']
		grouped_moves = groupby(sorted(self, key=lambda m: [f.id for f in m._key_assign_picking()]), key=lambda m: [m._key_assign_picking()])
		for group, moves in grouped_moves:
			moves = self.env['stock.move'].concat(*list(moves))
			for move in moves:
				new_picking = False
				picking = move._search_picking_for_assignation()
				if picking:
					if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
						picking.write({
							'partner_id': False,
							'origin': False,
						})
				else:
					new_picking = True
					picking = Picking.create(move._get_new_picking_values())

				move.write({'picking_id': picking.id})
				move._assign_picking_post_process(new=new_picking)
		return True