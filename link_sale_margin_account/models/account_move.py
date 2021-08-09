# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	purchase_price = fields.Float(string='Cost', digits='Product Price', readonly=True)