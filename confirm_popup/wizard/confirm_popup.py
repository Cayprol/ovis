# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)
class ConfirmPopup(models.TransientModel):

	_name = 'confirm.popup'
	_description = 'Wizard to log note for action.'

	note = fields.Text('Note', help="Reason of action.")

	def action_confirm(self):
		# .get() are non-required context
		parent_model = self._context.get('parent_model')
		parent_id = self._context.get('parent_id') # This could be a list of ids or single integer, .browse() takes either
		method = self._context.get('method')
		method_args = self._context.get('method_args', [])
		method_kwargs = self._context.get('method_kwargs', {})
		log_title = self._context.get('log_title')
		force_note = self._context.get('force_note')
		return_vals = self._context.get('return_vals')

		if not method and return_vals == 'method':
			raise exceptions.ValidationError(_('No method to run, returning values cannot be method.'))

		if parent_model and parent_id:
			recordset = self.env[parent_model].browse(parent_id)

		msg = "<b>{}</b><br/>{}".format(log_title, self.note)
		if force_note and not self.note:
			raise exceptions.UserError(_('Must have a reason for this action.'))
		elif self.note:
			recordset.message_post(body=msg)

		if recordset and method:
			run = getattr(recordset, method)(*method_args, **method_kwargs)

		if return_vals == 'method':
			return run
		elif return_vals == 'reload':
			return {'type': 'ir.actions.client','tag': 'reload'}
		else:
			return return_vals or {'type': 'ir.actions.client','tag': 'reload'}

	@api.constrains('note')
	def _check_note_isspace(self):
		if self.note and self.note.isspace():
			raise exceptions.UserError(_('Note cannot be white spaces.'))