# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

class SaleOrder(models.Model):
	_inherit = 'sale.order'
	"""
	Field 'scheduled_date' provided by standard Odoo. It is not editable.
	Module 'sale_multi_delivery_date' allow user to manually edit this field.
	This method is overriden to pass 'scheduled_date' from SOL to work with custom quotation-to-sale-order flow.
	"""
	def _prepare_order_line(self, order_line, option=False):
		pseudo_order_lines = super(SaleOrder, self)._prepare_order_line(order_line)
		if not option:
			for line, o2m_line in zip(order_line, pseudo_order_lines):
				o2m_line[2].update({'scheduled_date': line.scheduled_date})
		return pseudo_order_lines