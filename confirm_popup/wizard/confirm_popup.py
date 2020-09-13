# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class ConfirmPopup(models.TransientModel):

	_name = 'confirm.popup'
	_description = 'Wizard to log note for action.'

	note = fields.Text('Note', help="Reason of action.")

	def action_confirm(self):
		# .get() are non-required context
		parent_model = self._context.get('parent_model')
		parent_id = self._context.get('parent_id')
		action_title = self._context.get('action_title')
		action_parameter = self._context.get('action_parameter')
		action = self._context['action']
		force_note = self._context.get('force_note')
		result = self._context.get('result')

		if parent_model and parent_id:
			record = self.env[parent_model].browse(parent_id)

		msg = "{}<br/>{}".format(action_title, self.note)
		if force_note and not self.note:
			raise exceptions.UserError(_('Must have a reason for this action.'))

		record.message_post(body=msg)
		run = getattr(record, action)(action_parameter) if action_parameter else getattr(record, action)()

		if result == 'action_result':
			return run
		elif result is not None:
			return result
		else:
			return {'type': 'ir.actions.client','tag': 'reload'} 

	@api.constrains('note')
	def _check_note_isspace(self):
		if self.note and self.note.isspace():
			raise exceptions.UserError(_('Note cannot be white spaces.'))