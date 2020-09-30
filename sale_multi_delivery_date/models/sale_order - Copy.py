# -*- coding: utf-8 -*-
# This file is override module sale_stock/models/sale_order.py
from odoo import models, fields, api
from collections import defaultdict
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)
class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	# All fields computed by _compute_qty_at_date, invsersable, and stored.
	# All of these fields must have the same compute, inverse, store value to avoid compute_sudo() inconsistency.
	virtual_available_at_date = fields.Float(compute='_compute_qty_at_date', inverse='_inverse_qty_at_date', store=True)
	scheduled_date = fields.Datetime(compute='_compute_qty_at_date', inverse='_inverse_qty_at_date', store=True)
	free_qty_today = fields.Float(compute='_compute_qty_at_date', inverse='_inverse_qty_at_date', store=True)
	qty_available_today = fields.Float(compute='_compute_qty_at_date', inverse='_inverse_qty_at_date', store=True)
	warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_qty_at_date', inverse='_inverse_qty_at_date', store=True)


	def _calculate_latest_schedule_date(self, recordsets):
		no_false_scheduled_dates = [scheduled_date for scheduled_date in recordsets.mapped('scheduled_date') if scheduled_date]
		if no_false_scheduled_dates:
			return max(no_false_scheduled_dates)
		else:
			return fields.datetime.now()

	# Inverse the computed field in sale order line, this function controls, when SOL scheduled_date is changed,
	# the SO commitment_date should changed to the latest, SOL scheduled_date
	def _inverse_qty_at_date(self):
		for line in self:
			_logger.warning("Inverse entered")

			if not line.scheduled_date:
				_logger.warning("line.scheduled_date is False")
				SOLs = self.search([('order_id', '=', line.order_id.id)])
				latest_schedule_date = self._calculate_latest_schedule_date(SOLs)
				line.order_id.commitment_date = latest_schedule_date
				# line.scheduled_date = fields.datetime.now()

			elif line.order_id.commitment_date and line.order_id.commitment_date > line.scheduled_date:
				_logger.warning("commitment > scheduled_date, {} > {}".format(line.order_id.commitment_date, line.scheduled_date))
				SOLs = self.search([('order_id', '=', line.order_id.id)])
				scheduled_dates = SOLs.mapped('scheduled_date')
				no_false_scheduled_dates = [scheduled_date for scheduled_date in scheduled_dates if scheduled_date]
				if no_false_scheduled_dates:
					line.order_id.commitment_date = max(no_false_scheduled_dates)
				else:
					# Whenn all scheduled_date are deleted (begin False)
					line.order_id.commitment_date = fields.datetime.now()
			
			elif line.order_id.commitment_date and line.order_id.commitment_date < line.scheduled_date:
				_logger.warning("commitment < scheduled_date, {} < {}".format(line.order_id.commitment_date, line.scheduled_date))
				line.order_id.commitment_date = line.scheduled_date

			else:
				_logger.warning("scheduled_date is {}".format(line.scheduled_date))
				line.update({'scheduled_date': line.scheduled_date})
				SOLs = self.search([('order_id', '=', line.order_id.id)])
				latest_schedule_date = self._calculate_latest_schedule_date(SOLs)
				_logger.warning("latest_schedule_date is {}".format(latest_schedule_date))
				line.order_id.commitment_date = latest_schedule_date

	# Standard Odoo method, rewriting this method is easier than inheriting. 
	@api.depends('product_id', 'customer_lead', 'product_uom_qty', 'order_id.warehouse_id', 'order_id.commitment_date')
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
			if not line.display_qty_widget:
				continue
			line.warehouse_id = line.order_id.warehouse_id

			if line.order_id.commitment_date:
				if line.scheduled_date and line.order_id.commitment_date >= line.scheduled_date:  # New if clause for distinguishing New() and existed SOL.
					_logger.warning("1 {}".format(line.scheduled_date))
					date = line.scheduled_date
				else:
					_logger.warning("2 {}".format(line.order_id.commitment_date))
					date = line.order_id.commitment_date
			else:
				confirm_date = line.order_id.date_order if line.order_id.state in ['sale', 'done'] else fields.datetime.now()
				date = confirm_date + timedelta(days=line.customer_lead or 0.0)
				_logger.warning("3 {}".format(date))

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
				_logger.warning("4 scheduled_date is {}".format(scheduled_date))
				line.scheduled_date = scheduled_date
				qty_available_today, free_qty_today, virtual_available_at_date = qties_per_product[line.product_id.id]
				line.qty_available_today = qty_available_today - qty_processed_per_product[line.product_id.id]
				line.free_qty_today = free_qty_today - qty_processed_per_product[line.product_id.id]
				line.virtual_available_at_date = virtual_available_at_date - qty_processed_per_product[line.product_id.id]
				qty_processed_per_product[line.product_id.id] += line.product_uom_qty
			treated |= lines
		remaining = (self - treated)

		_logger.warning("remaining type {}, {}".format(type(remaining), remaining))
		for r in remaining:
			r.virtual_available_at_date = False
			r.scheduled_date = r.scheduled_date # This line must be present, when SOL are stil New(), if not assigned, error occurs.
			r.free_qty_today = False
			r.qty_available_today = False
			r.warehouse_id = False
		# remaining.virtual_available_at_date = False
		# remaining.scheduled_date = False
		# remaining.free_qty_today = False
		# remaining.qty_available_today = False
		# remaining.warehouse_id = False