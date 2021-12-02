# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class ConfirmPopup(models.TransientModel):

	_name = 'confirm.popup'
	_description = 'Wizard to log note for action.'

	note = fields.Html('Note', help='Reason of action.')

	def action_confirm(self):
		title = self._context.get('title', _('Confirm Memo'))
		run_action = self._context.get('run_action')
		args = self._context.get('args', [])
		kwargs = self._context.get('kwargs', {})
		if run_action:
			recordset = self.env[self._context.get('model')].browse(self._context.get('res_id')) # This could be a list of ids or single integer, .browse() takes either
			run = getattr(recordset, run_action)(*args, **kwargs)

		if not self.note.striptags(): # striptags() is built-in method for class Markup
			pass
		else:
			msg = "<b>{title}</b><br/>{note}".format(title=title, note=self.note)
			recordset.message_post(body=msg)

		return run

