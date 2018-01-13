# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherited(models.Model): 

	_inherited = 'sale.order'

	passed_override_write_function = fields.Boolean(string='Has passed our super method')

	@api.model
	def create(self, values):
		record = super(sale_order, self).create(values)
		record['passed_override_write_function'] = True
		print 'Passed this function. passed_override_write_function value: ' + str(record['passed_override_write_function'])

	return record

	# @api.model
	# def create(self, vals):
	# 	if vals.get('name', _('New')) == _('New'):
	# 		if 'company_id' in vals:
	# 			vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
	# 		else:
	# 			vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')

