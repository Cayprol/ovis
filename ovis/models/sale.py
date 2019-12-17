# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):

	_inherit = 'sale.order'

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

	@api.depends('order_line.tally')
	def _compute_tally(self):
		for order in self:
			notified = [line.tally for line in order.order_line]
			order.update({'tally': all(notified)})

	def action_draft(self):
		super(SaleOrder, self).action_draft()
		for line in self.order_line:
			line.update({'tally': False})
		return True


	tally = fields.Boolean("Tally", compute="_compute_tally", store=True, readonly=True, help="This field indicates all order lines associated to this order are notified for tally or not.")


class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	tally = fields.Boolean("Tally", help="This field indicates the order line has been notified for tally or not.")