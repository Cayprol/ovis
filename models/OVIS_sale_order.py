# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherited(models.Model): 

	_inherit = 'sale.order'

	material_prepare = fields.Boolean(string='Material Prepare')

	# Adding a state to exisiting states
	state = fields.Selection(selection_add=[('material_prepare','Material Preparing')])

	# creating order in certain state
	@api.one
	def action_material_prepare(self):
		self.state = 'material_prepare'

		



