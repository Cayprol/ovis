# -*- coding: utf-8 -*-
from odoo import api, fields, models

class InheritPartner(models.Model):

	_inherit = 'res.partner'

	forwarder = fields.Boolean(string='Is a Forwarder', default=False, help="Check this box if this contact is a forwarder. It can be selected in delivery orders.")


