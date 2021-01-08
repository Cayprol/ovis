# -*- coding: utf-8 -*-

from odoo import fields, models

class Company(models.Model):
	_inherit = 'res.company'

	default_invoice_policy = fields.Selection([
		('order', 'Invoice what is ordered'),
		('delivery', 'Invoice what is delivered')
		], 'Invoicing Policy',
		default='order',
		default_model='product.template')

	force_invoice_policy = fields.Boolean('Force Policy')