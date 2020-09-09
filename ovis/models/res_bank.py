# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

# class ResPartnerBank(models.Model):

# 	_inherit = 'res.partner.bank'

# 	_rec_name = 'nick_name'

# 	@api.model
# 	def create(self, values):
# 		record = super(ResPartnerBank, self).create(values)
# 		if not values['nick_name']:
# 			record['nick_name'] = record['acc_number']
# 		return record

# 	nick_name = fields.Char(string="Nick Name", help="Nick Name for bank accounts to be recognized easily.")


# class AccountJournal(models.Model):
# 	_inherit = 'account.journal'

# 	account_nick_name = fields.Char(related='bank_account_id.nick_name', readonly=False)

class Bank(models.Model):

	_inherit = 'res.bank'

	name = fields.Char(required=True, translate=True)