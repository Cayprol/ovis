# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):

	_inherit = 'account.move'
	

	# Potentially cause problem because invoice_partner_bank_id.journal_id is One2many. 
	def action_invoice_register_payment(self):
		return self.env['account.payment'].\
			with_context(active_ids=self.ids, active_model='account.move', active_id=self.id, default_journal_id=self.invoice_partner_bank_id.journal_id.id).\
			action_register_payment()