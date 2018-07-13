# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritSaleOrder(models.Model):

	_inherit = 'sale.order'

	user_company_id = fields.Many2one('res.company', 'User Current Company')

	match = fields.Boolean(string='Match')

	@api.multi
	@api.onchange('user_company_id', 'company_id', 'match')
	def check_match(self):
		self.ensure_one()
		if self.user_company_id != self.company_id:
			self.match = False
		else:
			self.match = True