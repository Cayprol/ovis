# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class SaleOrderInherited(models.Model): 

# 	_inherit = 'sale.order'

# 	material_work_order = fields.Boolean(string='MWO')

# 	@api.model
# 	def create(self, values):
# 		record = super(sale_order, self).create(values)
# 		if record['material_work_order'] == True:
# 			pass
# 		else:
# 			pass

# 	return record

	# @api.model
	# def create(self, vals):
	# 	if vals.get('name', _('New')) == _('New'):
	# 		if 'company_id' in vals:
	# 			vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
	# 		else:
	# 			vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')

