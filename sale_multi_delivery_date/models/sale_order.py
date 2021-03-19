# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from collections import defaultdict

import pytz

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# Adding the compute method
	commitment_date = fields.Datetime('Delivery Date', copy=False, readonly=True, compute='_compute_latest_delivery_date',
										help="This is the delivery date promised to the customer. "
											 "If set, the delivery order will be scheduled based on "
											 "this date rather than product lead times.")

	# Change 'commitment_date' to the latest 'scheduled_date' in 'order_line'
	@api.depends('order_line.scheduled_date')	
	def _compute_latest_delivery_date(self):
		for record in self:
			times = list(filter(None, record.order_line.mapped('scheduled_date')))
			latest = False if not times else max(times)
			record.commitment_date = latest

	@api.onchange('commitment_date')
	def _onchange_commitment_date(self):
		""" Warn if the commitment dates is sooner than the expected date """
		# 'commitment_date' and 'expected_date' are datetime, 'commitment_date' is set by 'scheduled_date', 'scheduled_date' has been overriden from Datetime to Date.
		# By default, conversion of Date to Datetime is set at midnight, which triggers warning when 'expected_date' is at a time later on the same day.
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
	
	# Override field type 'scheduled_date' from Datetime to Date, 
	# If _compute_qty_at_date() has remaining.scheduled_date = False, when progressing 'state', 'scheduled_date' gets set to False.
	scheduled_date = fields.Date(string='Delivery Date', help='Individual delivery date for sale order lines. This field change commitment_date on sale order.')

	@api.depends('product_id', 'customer_lead', 'product_uom_qty', 'product_uom', 'order_id.warehouse_id', 'order_id.commitment_date')
	def _compute_qty_at_date(self):
		""" Compute the quantity forecasted of product at delivery date. There are
		two cases:
		 1. The quotation has a commitment_date, we take it as delivery date
		 2. The quotation hasn't commitment_date, we compute the estimated delivery
			date based on lead time"""
		qty_processed_per_product = defaultdict(lambda: 0)
		grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
		# We first loop over the SO lines to group them by warehouse and schedule
		# date in order to batch the read of the quantities computed field.
		for line in self:
			if not (line.product_id and line.display_qty_widget):
				continue
			line.warehouse_id = line.order_id.warehouse_id

			# 'scheduled_date' has priority to be date
			if line.scheduled_date:
				date = line.scheduled_date
			elif line.order_id.commitment_date:
				date = line.order_id.commitment_date

			else:
				date = line._expected_date()
			grouped_lines[(line.warehouse_id.id, date)] |= line

		treated = self.browse()
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
				if line.product_uom and line.product_id.uom_id and line.product_uom != line.product_id.uom_id:
					line.qty_available_today = line.product_id.uom_id._compute_quantity(line.qty_available_today, line.product_uom)
					line.free_qty_today = line.product_id.uom_id._compute_quantity(line.free_qty_today, line.product_uom)
					line.virtual_available_at_date = line.product_id.uom_id._compute_quantity(line.virtual_available_at_date, line.product_uom)
				qty_processed_per_product[line.product_id.id] += line.product_uom_qty
			treated |= lines

		remaining = (self - treated)
		remaining.virtual_available_at_date = False
		# remaining.scheduled_date = False
		remaining.free_qty_today = False
		remaining.qty_available_today = False
		remaining.warehouse_id = False