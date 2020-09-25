# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Bank(models.Model):

	_inherit = 'res.bank'

	name = fields.Char(required=True, translate=True)