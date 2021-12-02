# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from collections import defaultdict

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# Adding the compute method
	commitment_date = fields.Datetime(
		'Delivery Date', 
		copy=False, 
		states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
		compute='_compute_commitment_date',
		help="This is the delivery date promised to the customer. "
			 "If set, the delivery order will be scheduled based on "
			 "this date rather than product lead times.")

	# @api.onchange('expected_date')
	# def _onchange_expected_date(self):
	# 	pass

	@api.depends('order_line.scheduled_date')
	def _compute_commitment_date(self):
		for record in self:
			datetimes = list(filter(None, record.order_line.mapped('scheduled_date')))
			latest = fields.Datetime.now() if not datetimes else max(datetimes)
			record.commitment_date = latest

	@api.onchange('commitment_date')
	def _onchange_commitment_date(self):
		""" 
		Warn if the commitment dates is sooner than the expected date
		This method is overriden because order_line.scheduled_date is overridden from type Datetime to Date.
		The default date and datetime conversion is at mid-night, 
		self.commitment_date will always be mid-night of the latest order_line.schedule_date by the _compute_commitment_date method.
		This would cause all newly created SOL to trigger this warning, despite the fact they are on the same current date.
		So datetime comparison should be set to date comparison to mitigate this problem.
		"""
		if (self.commitment_date and self.expected_date and self.commitment_date.date() < self.expected_date.date()):
			return {
				'warning': {
					'title': _('Requested date is too soon.'),
					'message': _("The delivery date is sooner than the expected date."
								 "You may be unable to honor the delivery date.")
				}
			}


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'
	
	# Override field type 'scheduled_date' from Datetime to Date
	# If _compute_qty_at_date() has remaining.scheduled_date = False, when progressing 'state', 'scheduled_date' gets set to False.
	scheduled_date = fields.Date(string='Delivery Date', help='Individual delivery date for sale order lines. This field change commitment_date on sale order.')
	# store=True, readonly=False, compute="_compute_qty_at_date" works, but inconsistent 'compute_sudo' error occurs

	@api.depends(
		'product_id', 'customer_lead', 'product_uom_qty', 'product_uom', 
		'order_id.commitment_date',
		'move_ids', 'move_ids.forecast_expected_date', 'move_ids.forecast_availability')
	def _compute_qty_at_date(self):
		""" Compute the quantity forecasted of product at delivery date. There are
		two cases:
		 1. The quotation has a commitment_date, we take it as delivery date
		 2. The quotation hasn't commitment_date, we compute the estimated delivery
			date based on lead time"""
		treated = self.browse()
		# If the state is already in sale the picking is created and a simple forecasted quantity isn't enough
		# Then used the forecasted data of the related stock.move
		for line in self.filtered(lambda l: l.state == 'sale'):
			if not line.display_qty_widget:
				continue
			moves = line.move_ids.filtered(lambda m: m.product_id == line.product_id)
			line.forecast_expected_date = max(moves.filtered("forecast_expected_date").mapped("forecast_expected_date"), default=False)
			line.qty_available_today = 0
			line.free_qty_today = 0
			for move in moves:
				line.qty_available_today += move.product_uom._compute_quantity(move.reserved_availability, line.product_uom)
				line.free_qty_today += move.product_id.uom_id._compute_quantity(move.forecast_availability, line.product_uom)
			# line.scheduled_date = line.scheduled_date or line.order_id.commitment_date or line._expected_date()
			line.virtual_available_at_date = False
			treated |= line

		qty_processed_per_product = defaultdict(lambda: 0)
		grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
		# We first loop over the SO lines to group them by warehouse and schedule
		# date in order to batch the read of the quantities computed field.
		for line in self.filtered(lambda l: l.state in ('draft', 'sent')):
			if not (line.product_id and line.display_qty_widget):
				continue
			# grouped_lines[(line.warehouse_id.id, line.order_id.commitment_date or line._expected_date())] |= line
			grouped_lines[(line.warehouse_id.id, line.scheduled_date or line.order_id.commitment_date or line._expected_date())] |= line

		for (warehouse, scheduled_date), lines in grouped_lines.items():
			product_qties = lines.mapped('product_id').with_context(to_date=scheduled_date, warehouse=warehouse).read([
				'qty_available',
				'free_qty',
				'virtual_available',
			])
			qties_per_product = {
				product['id']: (product['qty_available'], product['free_qty'], product['virtual_available'])
				for product in product_qties
			}
			for line in lines:
				line.scheduled_date = scheduled_date
				qty_available_today, free_qty_today, virtual_available_at_date = qties_per_product[line.product_id.id]
				line.qty_available_today = qty_available_today - qty_processed_per_product[line.product_id.id]
				line.free_qty_today = free_qty_today - qty_processed_per_product[line.product_id.id]
				line.virtual_available_at_date = virtual_available_at_date - qty_processed_per_product[line.product_id.id]
				line.forecast_expected_date = False
				product_qty = line.product_uom_qty
				if line.product_uom and line.product_id.uom_id and line.product_uom != line.product_id.uom_id:
					line.qty_available_today = line.product_id.uom_id._compute_quantity(line.qty_available_today, line.product_uom)
					line.free_qty_today = line.product_id.uom_id._compute_quantity(line.free_qty_today, line.product_uom)
					line.virtual_available_at_date = line.product_id.uom_id._compute_quantity(line.virtual_available_at_date, line.product_uom)
					product_qty = line.product_uom._compute_quantity(product_qty, line.product_id.uom_id)
				qty_processed_per_product[line.product_id.id] += product_qty
			treated |= lines
		remaining = (self - treated)
		remaining.virtual_available_at_date = False
		# remaining.scheduled_date = False
		remaining.forecast_expected_date = False
		remaining.free_qty_today = False
		remaining.qty_available_today = False