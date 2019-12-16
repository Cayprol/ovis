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
