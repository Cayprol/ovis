# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

"""
	This entire py file is WIP,
	Create warning/notification if Delivery Date is changed in Sale Order in state 'sale'
"""


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	# def write(self, values):
	# 	if values.get('scheduled_date'):
	# 		for line in self:
	# 			_logger.warning("depends triggered with ID {}".format(line.id))
	# 			if line.state in ['sale', 'done']:
	# 				_logger.warning("line state is in sale or done, line ID {}".format(line.id))

	# 				moves = self.env['stock.move'].search([('sale_line_id', '=', line.id)])

	# 				_logger.warning("moves with corresponding sale_line_id {}".format(moves))

	# 				pickings = moves.mapped('picking_id')

	# 				_logger.warning("pickings type {}, pickings {}".format(type(pickings), pickings))

	# 				SO = line.order_id.name

	# 				_logger.warning("SO name {}".format(SO))

	# 				scheduled_date_changed = "<b>{}</b> scheduled date was changed.".format(SO)
	# 				pickings.message_post(body=scheduled_date_changed)

	# 	return super(SaleOrderLine, self).write(values)


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	def _track_subtype(self, init_values):
		_logger.warning("run")
		self.ensure_one()
		if 'commitment_date' in init_values and self.state in ['sale', 'done']:
			_logger.warning("triggered")
			return self.env.ref('link_change_order_multi_delivery_date.mt_change_scheduled_date')
		return super(SaleOrder, self)._track_subtype(init_values)