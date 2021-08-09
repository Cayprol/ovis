# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MrpBom(models.Model):
	_inherit = 'mrp.bom'

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			vals['company_id'] = False
		return super(MrpBom, self).create(vals_list)

	# We cannot just change 'default' attribute to None or False, 
	# there's other method that would force to fill in company_id if the field isn't filled 
	# company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: None)