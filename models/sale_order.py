# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritSaleOrder(models.Model):

	_inherit = 'sale.order'

	user_company_id = fields.Many2one('res.company', 'User Current Company')

	match = fields.Boolean(string='Match', default=False)

	# @api.onchange('user_company_id')
	# @api.multi
	# def _check_match(self):
	# 	if self.company_id != self.user_company_id:
	# 		self.match = False

	# 	else:
	# 		self.match = True