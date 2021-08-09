# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _ 

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
			if line.approved_order_id:
				line.qty_delivered_method = 'manual'

	def _inverse_invoice_qty(self):
		for line in self:
			if line.approved_order_id:
				line.qty_invoiced = line.qty_invoiced


