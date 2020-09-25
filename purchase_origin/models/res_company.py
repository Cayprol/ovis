# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
	_inherit = "res.company"

	po_origin = fields.Selection([
		('standard', 'Reordering rule'), 
		('sales', 'Sales Order'), 
		('delivery', 'Delivery Order')], 
		string='Origin Control', 
		default='standard')