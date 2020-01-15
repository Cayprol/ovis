# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):

	_inherit = 'account.move'
	
	# Add default_journal_id to be selected 'Bank Account' under 'Payments' section.
	# Potentially cause problem because invoice_partner_bank_id.journal_id is One2many. 
	def action_invoice_register_payment(self):
		return self.env['account.payment'].\
			with_context(active_ids=self.ids, active_model='account.move', active_id=self.id, default_journal_id=self.invoice_partner_bank_id.journal_id.id).\
			action_register_payment()

	# Duplicated invoice name(Number) based on original, this help differ it from Manually created name(/).
	def copy(self, default=None):
		self.ensure_one()
		if self.type == 'out_invoice' and self.state == 'posted':
			# name = self.env['ir.sequence'].next_by_code('invoice.duplicate') or '//'
			name = "C" + self.name
			default = {'name': name}
		return super(AccountMove, self).copy(default)
