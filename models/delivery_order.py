# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritStockMoveLine(models.Model):

	_inherit = 'stock.move.line'

	_order = 'carton asc'

	net_weight = fields.Float(related='move_id.net_weight', readonly=True)
	gross_weight = fields.Float(related='move_id.gross_weight', readonly=True)
	carton = fields.Char(related='move_id.carton', readonly=True)

	weight_unit_id = fields.Selection(related='picking_id.weight_unit', readonly=True)

class InheritStockMove(models.Model):

	_inherit = 'stock.move'

	_order = 'carton asc'

	net_weight = fields.Float(string='Net Weight', help='Sum of the net weight of each line product')
	gross_weight = fields.Float(string='Gross Weight', help='Sum of the total weight of each line product')
	carton = fields.Char(string='Carton No.', help='Carton number each product is placed in.')


class InheritStockPicking(models.Model):

	_inherit = 'stock.picking'

	signature = fields.Selection([('ovis','OVIS Enterprise Co.,Ltd.'),('ovis_int','OVIS Enterprise Int\'l Co.,Ltd.'),('pangu','Pangu Electronics')],
									string='Signature',
									default='ovis',
									)
	weight_unit = fields.Selection([('kg', 'Kilogram(s)'), ('lb', 'Pound(s)'), ('g', 'Gram(s)')], string='Weight Unit', default='kg')
	
	carton_total = fields.Integer(string='Cartons')
	initial_total = fields.Float(string='Initial Demend', compute='_compute_amount', store=False)
	reserved_total = fields.Float(string='Reservered', compute='_compute_amount', store=False)
	done_total = fields.Float(string='Done', compute='_compute_amount')
	net_weight_total = fields.Float(string='Net Weight', compute='_compute_amount', store=False)	
	gross_weight_total = fields.Float(string='Gross Weight', compute='_compute_amount', store=False)	

	product_uom_id = fields.Many2one(related='move_line_ids.product_uom_id', readonly=True)

	remarks = fields.Text(string='REMARKS', help='Remarks for D/O.')

	shipping_id = fields.Many2one('stock.picking.shipping', string='Shipper', help="Shipping details")

	shipping_to = fields.Many2one('res.partner', 'Ship To', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

	@api.one
	@api.depends('move_lines.net_weight', 'move_lines.gross_weight', 'move_lines.product_uom_qty', 'move_lines.reserved_availability','move_lines.quantity_done')
	def _compute_amount(self):
		self.net_weight_total = sum(line.net_weight for line in self.move_lines)
		self.gross_weight_total = sum(line.gross_weight for line in self.move_lines)
		self.done_total = sum(line.quantity_done for line in self.move_lines)
		self.initial_total = sum(line.product_uom_qty for line in self.move_lines)
		self.reserved_total = sum(line.reserved_availability for line in self.move_lines)

	# @api.multi
	# def _compute_show_check_weight(self):
	# 	for picking in self:
	# 		has_moves_to_reserve = any(
	# 			move.state in ('waiting', 'confirmed', 'partially_available') and
	# 			float_compare(move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding)
	# 			for move in picking.move_lines
	# 		)
	# 		picking.show_check_availability = picking.is_locked and picking.state in ('confirmed', 'waiting', 'assigned') and has_moves_to_reserve

class StockPickingShipping(models.Model):

	_name = 'stock.picking.shipping'

	_rec_name = 'name'


	name = fields.Char(string='Display Name', compute="_name_create", readonly=True, help="Display name of this shipping method.")
	
	departure_id = fields.Many2one('res.country', string='Departure', required="True", help="Departure location of the Delivery Slip.")
	destination_id = fields.Many2one('res.country', string='Destination', required="True", help="Destination location of the Delivery Slip.")
	marks_made_in_id = fields.Many2one('res.country', string='Made In', required="True", help="Where the contained items are Made in.")
	
	forwarder_id = fields.Many2one('res.partner', string='Forwarder', required="True", help="Name of the Forwarder.")

	way = fields.Char(string='By', help="By air or by sea.")
	sailing = fields.Char(string='Sailing On', help="Which port.")
	marks_carton = fields.Char(string='C/NO.', help="Marks & NO. of total cartons.")

	@api.one
	@api.depends('forwarder_id', 'departure_id', 'destination_id')
	def _name_create(self):
		_output = {
					"forwarder":"",
					"departure":"",
					"destination":"",
					}

		if self.forwarder_id.name != False:
			_output["forwarder"]=self.forwarder_id.name

		else:
			_output["forwarder"]=" "

		if self.departure_id.code != False:
			_output["departure"]=self.departure_id.code

		else:
			_output["departure"]=" "

		if self.destination_id.code != False:
			_output["destination"]=self.destination_id.code

		else:
			_output["destination"]=" "

		self.name = _output["forwarder"]+" from "+_output["departure"]+" to "+_output["destination"]