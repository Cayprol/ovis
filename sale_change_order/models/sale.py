# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _ 
import logging
_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

	_inherit = 'sale.order'

	def action_change_order(self):
		self.ensure_one()

		_logger.warning("Order ID: {}, OrderLine IDs {}".format(self.id, self.order_line))
		_logger.warning("Active model name is {}".format(self._name))

		return {
			'type': 'ir.actions.act_window',
			'res_model': 'change.order',
			'views': [(self.env.ref('sale_change_order.change_order_form').id, 'form')],
			'view_id': self.env.ref('sale.view_order_form').id,
			'context': {'default_sale_order_id': self.id,
						# 'default_changed_sale_order_line': self._prepare_changed_sale_order_line(self.order_line)
						}
		}

	# def _prepare_changed_sale_order_line(self, order_line):
	# 	order_lines = [
	# 		(0, False, {
	# 			'order_id': self.id,
	# 			'product_id': line.product_id.id,
	# 			'product_uom_qty': line.product_uom_qty,
	# 			'product_uom': line.product_uom.id,
	# 				}
	# 			) for line in order_line ]

	# 	return order_lines

	def _compute_change_order_count(self):
		recordsets = self.env['change.order'].search([('sale_order_id','=',self.id)])
		count = len(recordsets)
		self.change_order_count = count

	change_order_count = fields.Integer(string='Change Order Count', compute='_compute_change_order_count', readonly=True)

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	order_id = fields.Many2one('sale.order', string='Order Reference', required=False, ondelete='cascade', index=True, copy=False)
	approved_order_id = fields.Many2one('change.order', string='Change Order', ondelete='cascade', index=True, copy=False)
	original_order_id = fields.Many2one('change.order', string='Change Order', ondelete='cascade', index=True, copy=False)