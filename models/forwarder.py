# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritResPartner(models.Model):

	_inherit = 'res.partner'

	forwarder = fields.Boolean(string='Is a Forwader', default=False, help="Check this box if this contact is a forwarder.")
