# -*- coding: utf-8 -*-
from odoo import api, fields, models

class InheritCountryState(models.Model):

	_inherit = 'res.country.state'

	# add translate=True
	name = fields.Char(string='State Name', required=True, translate=True, help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')

	# add translate=True
	code = fields.Char(string='State Code', help='The state code.', required=True, translate=True)