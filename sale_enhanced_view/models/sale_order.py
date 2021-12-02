# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	display_require_signature = fields.Boolean(string='Display Online Signature', compute='_get_display_require_signature', help='Technical field for xml domain use to show Online Signature or not.')
	display_require_payment = fields.Boolean(string='Display Online Payment', compute='_get_display_require_payment', help='Technical field for xml domain use to show Online Payment or not.')

	@api.depends('company_id.portal_confirmation_sign')
	def _get_display_require_signature(self):
		for record in self:
			record.display_require_signature = record.company_id.portal_confirmation_sign

	@api.depends('company_id.portal_confirmation_pay')
	def _get_display_require_payment(self):
		for record in self:
			record.display_require_payment = record.company_id.portal_confirmation_pay