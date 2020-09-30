# -*- coding: utf-8 -*-
from odoo import models, fields
from itertools import groupby

class stock_move(models.Model):
	_inherit = 'stock.move'

	# Pass 'date_expected' in 'stock.move' to 'scheduled_date' in 'stock.picking'
	# This field was passed from 'scheduled_date' in 'sale.order.line' to 'date_expected' in 'stock.move'
	def _get_new_picking_values(self):
		values = super(stock_move,self)._get_new_picking_values()
		values.update({'scheduled_date': self.date_expected})
		return values
		
	# Search Picking for move and assign to picking to move 
	def _search_picking_for_assignation(self):
		res = super(stock_move,self)._search_picking_for_assignation()
		if self.date_expected:
			picking = self.env['stock.picking'].search([
				('group_id', '=', self.group_id.id),
				('location_id', '=', self.location_id.id),
				('location_dest_id', '=', self.location_dest_id.id),
				('picking_type_id', '=', self.picking_type_id.id),
				('scheduled_date','=',self.date_expected),
				('printed', '=', False),
				('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
			return picking
		return res
	
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