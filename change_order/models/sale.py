# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _ 

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

	_inherit = 'sale.order'

	def action_create_change_sale_order(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'change.sale.order',
			'views': [(self.env.ref('change_order.change_sale_order_form').id, 'form')],
			'context': {'default_sale_order_id': self.id,},
		}

	def _compute_change_sale_order_count(self):
		for record in self:
			change_sale_orders = self.env['change.sale.order'].search([('sale_order_id','=',record.id)])
			count = len(change_sale_orders)
			record.change_sale_order_count = count

	change_sale_order_count = fields.Integer(string='Change Order Count', compute='_compute_change_sale_order_count', readonly=True)
	order_line_confirmed = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

	# If 1 or more CSO been done, new SOLs created. The invoices created by original SOLs must be linked to the new SOLs.
	@api.depends('order_line.invoice_lines')
	def _get_invoiced(self):
		for order in self:
			invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
			for change_sale_order in self.env['change.sale.order'].search([('sale_order_id','=',order.id),('state','=','done')]):
				original_invoices = change_sale_order.original_sale_order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
				invoices |= original_invoices

			order.invoice_ids = invoices
			order.invoice_count = len(invoices)

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	# required must be False, so when a change sale order is completed, the original SOL disassociates with SO which means it has no order_id.
	order_id = fields.Many2one('sale.order', string='Order Reference', required=False, ondelete='cascade', index=True, copy=False)

	# copy must be False, if a SO has been changed once, copy() the SO would duplicate all SOLs
	# These duplicated SOLs are not supposed to affect existing change sale order 
	approved_order_id = fields.Many2one('change.sale.order', string='Change Sale Order Approved', ondelete='cascade', index=True, copy=False)
	original_order_id = fields.Many2one('change.sale.order', string='Change Sale Order Original', ondelete='cascade', index=True, copy=False)

	# Add inserve logic
	qty_invoiced = fields.Float(
		compute='_get_invoice_qty', inverse='_inverse_invoice_qty', string='Invoiced Quantity', store=True, readonly=False,
		compute_sudo=True,
		digits='Product Unit of Measure')

	@api.depends('product_id', 'state', 'is_expense')
	def _compute_qty_delivered_method(self):
		# super from module 'sale_stock', because change_order depends list in __manifest__.py, 'sale_stock' is in front of 'sale'
		# execution seqeunce sale -> sale_stock -> change_order
		super(SaleOrderLine, self)._compute_qty_delivered_method() 
		for line in self:
			if (line.approved_order_id and line.state not in ['sale', 'done']) or (not line.order_id and line.original_order_id):
				line.qty_delivered_method = 'manual'

	@api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
	def _compute_qty_delivered(self):
		super(SaleOrderLine, self)._compute_qty_delivered()

		for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
			if line.qty_delivered_method == 'stock_move' and line.approved_order_id:
				qty = 0.0
				outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
				for move in outgoing_moves:
					if move.state != 'done':
						continue
					qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
				for move in incoming_moves:
					if move.state != 'done':
						continue
					qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
				# line.qty_delivered = qty
				line.qty_delivered = line.qty_delivered_manual + qty

	def _get_qty_procurement(self, previous_product_uom_qty=False):
		qty = super(SaleOrderLine, self)._get_qty_procurement(previous_product_uom_qty)
		if self.approved_order_id:
			qty += self.qty_delivered
		return qty

	def _inverse_invoice_qty(self):
		for line in self:
			if line.approved_order_id:
				line.qty_invoiced = line.qty_invoiced

	def unlink(self):
		for rec in self:
			if rec.state in ['sale', 'done', 'cancel']:
				raise exceptions.UserError(_("Confirmed sales order line cannot be deleted.\nCreate a change order."))

		return super(SaleOrderLine, self).unlink()