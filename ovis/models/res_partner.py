# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):

	_inherit = 'res.partner'

	# code_name = fields.Char(string='Code Name', help="Unique short name.")