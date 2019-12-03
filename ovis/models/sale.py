# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):

	_inherit = 'sale.order'

	# Checker field to determine an order being back order or not
	is_back_order = fields.Boolean('Back Order Status', compute="_back_order_check", store=True, default=False, help="This boolean field indicates whether this Sale Order has not yet delivered quantity or not.")

	def action_send(self):
		self.ensure_one()
		self.write({'state': 'sent'})
		return True

	def action_confirm_sale_order(self):
		view = self.env.ref('ovis.quote_order_form')
		wiz = self.env['quote.to.order'].create({})
		return {
			'name': _('Create Sales Order?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'quote.to.order',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wiz.id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,},
		}

	# Created for is_back_order field, a checker field meant to implement filter of Sales Back Order.
	@api.depends('order_line.product_uom_qty', 'order_line.qty_delivered', 'state')
	def _back_order_check(self):
		if self.state in ('sale', 'done'):
			diff = [ True if line.qty_delivered - line.product_uom_qty < 0 else False for line in self.order_line ]
			if any(diff):
				self.write({'is_back_order': True})
			else:
				self.write({'is_back_order': False})
		else:
			self.write({'is_back_order': False})
