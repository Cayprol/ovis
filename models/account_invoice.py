# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritAccountInvoice(models.Model):

	_inherit = 'account.invoice'

	amount_tax_signed = fields.Monetary(string='Tax Signed', store=True, readonly=True, compute='_compute_amount', currency_field='company_currency_id')

