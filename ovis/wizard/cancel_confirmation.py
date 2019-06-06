# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class CancelConfirmation(models.TransientModel):

	_name = 'cancel.confirmation'

	def action_confirm(self):

		parent_model = self._context['parent_model']
		parent_id = self._context['parent_id']

		return self.env[parent_model].browse(parent_id).action_cancel()
