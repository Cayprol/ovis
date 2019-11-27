# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class QuoteToOrder(models.TransientModel):

	_name = 'quote.to.order'

	note = fields.Text('Note', help="Log note. quotation -> order.")

	def _confirm(self, record):
		if hasattr(record, 'action_confirm'):
			record.action_confirm()
		elif hasattr(record, 'button_confirm'):
			record.button_confirm()
		else:
			raise exceptions.ValidationError('No valid action to execute.')		

	def action_confirm(self):
		parent_model = self._context['parent_model']
		parent_id = self._context['parent_id']
		rec = self.env[parent_model].browse(parent_id)
		if self.note and not self.note.isspace():
			msg = _("Confirm") + ": {}".format(self.note)
			self._confirm(rec)
			return rec.message_post(body=msg)

		else:
			self._confirm(rec)
			return False

