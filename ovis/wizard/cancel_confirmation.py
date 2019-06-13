# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class CancelConfirmation(models.TransientModel):

	_name = 'cancel.confirmation'

	notes = fields.Text(string='Note', help='Note to log in chatter.')

	def action_confirm(self):
		parent_model = self._context['parent_model']
		parent_id = self._context['parent_id']
		rec = self.env[parent_model].browse(parent_id)
		msg = "Reason to cancel: {}".format(self.notes)
		rec.action_cancel()
		return rec.message_post(body=msg)
