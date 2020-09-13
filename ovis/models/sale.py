# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

	_inherit = 'sale.order'

	@api.multi
	def action_cancel(self):
		self.ensure_one()
		return {
			'name': _('Cancel this record?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,
						'action_title': "Cancelling Reason:",
						'action_parameter': {'state': 'cancel'},
						'action': 'update',
						},
		}

	@api.multi
	def action_send(self):
		self.ensure_one()
		if self.state != 'draft':
			raise exceptions.ValidationError(_("Only draft state are allowed to be sent."))

		return {
			'name': _('Prepare this quotation to be sent?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,
						'action_title': "Send Memo:",
						'action_parameter': {'state': 'sent'},
						'action': 'update',
						},
		}

	@api.multi
	def action_create_so(self):
		self.ensure_one()
		return {
			'name': _('Create sale order based on this quotation?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,
						'action_title': "Sale Order Created: ",
						'action_parameter': {},
						'action': 'action_confirm',
						'force_note': True,
						'result': 'action_result'
						},
		}
		