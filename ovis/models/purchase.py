# -*- coding: utf-8 -*-

from odoo import models, exceptions, _

class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	def button_approve_2step(self, force=False):
		# Check any of the selected recordsets is not in 'draft' state
		for order in self:
			if order.state != 'to approve':
				raise exceptions.UserError(_("Only sent RFQ  are allowed to be sent."))
		return {
			'name': _('Approve this purchase order?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.ids,
						'method': 'button_approve',
						'method_kwargs': {'force': force},
						'log_title': _("Approve Memo:"),
						},
			}

	def button_send_2step(self):
		# Check any of the selected recordsets is not in 'draft' state
		for order in self:
			if order.state != 'draft':
				raise exceptions.UserError(_("Only unsent RFQ are allowed to be sent."))

		return {
			'name': _('Prepare this RFQ to be sent?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.ids,
						'method': 'write',
						'method_args': [{'state': 'sent'}],
						'log_title': _("Send Memo:"),
						},
			}

	def button_confirm_2step(self):
		for order in self:
			if order.state != 'sent':
				raise exceptions.UserError(_("There's RFQ/Purchase order not being RFQ Sent selected."))

		return {
			'name': _('Confirm Sent RFQ to be a Purchase Order?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'confirm.popup',
			'views': [(self.env.ref('confirm_popup.confirm_popup_form').id, 'form')],
			'view_id': self.env.ref('confirm_popup.confirm_popup_form').id,
			'target': 'new',
			'res_id': self.env['confirm.popup'].create({}).id,
			'context': {'parent_model': self._name,
						'parent_id': self.ids,
						'method': 'button_confirm',
						'log_title': _("Confirm Memo:"),
						'force_note': True
						},
			}

	def button_cancel_2step(self):
		force_note = False
		for order in self:
			if order.state == 'cancel':
				raise exceptions.UserError(_("Already cancelled RFQ/Purchase order is selected."))
			elif order.state in ['sent', 'to approve', 'purchase', 'done']:
				force_note = True

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
						'parent_id': self.ids,
						'method': 'button_cancel',
						'log_title': _("Cancelling Reason:"),
						'force_note': force_note
						},
			}
