# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class SaleOrder(models.Model):

	_inherit = 'sale.order'

	@api.multi
	def action_confirm(self):
		if self._get_forbidden_state_confirm() & set(self.mapped('state')):
			raise UserError(_(
				'It is not allowed to confirm an order in the following states: %s'
			) % (', '.join(self._get_forbidden_state_confirm())))

		for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
			order.message_subscribe([order.partner_id.id])

		sale_order = self.copy({
			'state': 'sale',
			'origin': self.name,
			'confirmation_date': fields.Datetime.now()
		})
		self._action_confirm()
		if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
			self.action_done()

		return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'sale.order',
				'target': 'current',
				'res_id': sale_order.id,
			}

	# Add draft to forbidden to confirm states
	def _get_forbidden_state_confirm(self):
		return {'done', 'cancel', 'draft'}

	@api.model
	def create(self, vals):
		if vals.get('state') == 'sale':
			vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
		else:
			vals['name'] = self.env['ir.sequence'].next_by_code('sale.quotation') or _('New')
		return super(SaleOrder, self).create(vals)
