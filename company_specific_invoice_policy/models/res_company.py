# -*- coding: utf-8 -*-

from odoo import fields, models

class Company(models.Model):
	_inherit = 'res.company'

	invoice_policy_forced = fields.Selection([
		('order', 'Invoice what is ordered'),
		('delivery', 'Invoice what is delivered')
		], 'Invoicing Policy Forced',
		default='order')

	force_invoice_policy = fields.Boolean('Force Policy')