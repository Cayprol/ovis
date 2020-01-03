# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartnerBank(models.Model):

	_inherit = 'res.partner.bank'

	_rec_name = 'nick_name'

	nick_name = fields.Char(string="Nick Name", required=True, help="Nick Name for bank accounts to be recognized easily.")


class AccountJournal(models.Model):
	_inherit = 'account.journal'

	account_nick_name = fields.Char(related='bank_account_id.nick_name', readonly=False)