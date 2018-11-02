# -*- coding: utf-8 -*-
from odoo import api, fields, models

class InheritCountryState(models.Model):

	_inherit = 'res.country.state'

	# add translate=True
	code = fields.Char(string='State Code', help='The state code.', required=True, translate=True)