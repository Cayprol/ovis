# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritPurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	invoice_create = fields.Boolean(string='Invoice Create', compute='_compute_creation')

	@api.multi
	def _compute_creation(self):
		self.ensure_one()
		if self.company_id.name != self.env.user.company_id.name:
			self.invoice_create = False
		else:
			self.invoice_create = True
