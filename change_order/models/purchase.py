# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _ 

class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	def action_create_change_purchase_order(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'change.purchase.order',
			'views': [(self.env.ref('change_order.change_purchase_order_form').id, 'form')],
			'context': {'default_purchase_order_id': self.id,},
		}

	def _compute_change_purchase_order_count(self):
		for record in self:
			change_purchase_orders = self.env['change.purchase.order'].search([('purchase_order_id','=',record.id)])
			count = len(change_purchase_orders)
			record.change_purchase_order_count = count

	change_purchase_order_count = fields.Integer(string='Change Order Count', compute='_compute_change_purchase_order_count', readonly=True)

	@api.depends('order_line.invoice_lines.move_id')
	def _compute_invoice(self):
		for order in self:
			invoices = order.mapped('order_line.invoice_lines.move_id')
			for change_purchase_order in self.env['change.purchase.order'].search([('purchase_order_id','=',order.id),('state','=','done')]):
				original_invoices = change_purchase_order.mapped('original_purchase_order_line.invoice_lines.move_id')
				invoices |= original_invoices
			order.invoice_ids = invoices
			order.invoice_count = len(invoices)

class PurchaseOrderLine(models.Model):

	_inherit = 'purchase.order.line'

	# required must be False, so when a change purchase order is completed, the original POL disassociates with PO which means it has no order_id.
	order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=False, ondelete='cascade')

	# copy must be False, if a PO has been changed once, copy() the PO would duplicate all POLs
	# These duplicated POLs are not supposed to affect existing change purchase order 
	approved_order_id = fields.Many2one('change.purchase.order', string='Change Purchase Order Approved', ondelete='cascade', index=True, copy=False)
	original_order_id = fields.Many2one('change.purchase.order', string='Change Purchase Order Original', ondelete='cascade', index=True, copy=False)

	# Add inverse logic
	qty_invoiced = fields.Float(compute='_compute_qty_invoiced', inverse='_inverse_qty_invoiced', string="Billed Qty", digits='Product Unit of Measure', store=True)

	"""
	This method is override the one in 'purchase_stock' by setting depends in __manifest__.py
	The purchase_stock _compute_qty_received_method is overriding what's in the purchase module.
	"""
	@api.depends('product_id')
	def _compute_qty_received_method(self):
		super(PurchaseOrderLine, self)._compute_qty_received_method()
		for line in self:
			if line.approved_order_id:
				line.qty_received_method = 'manual'

	def _inverse_qty_invoiced(self):
		for line in self:
			if line.approved_order_id:
				line.qty_invoiced = line.qty_invoiced
