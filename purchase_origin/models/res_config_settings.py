# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	po_origin = fields.Selection([
		('standard', 'Reordering rule'), 
		('sales', 'Sales Order'), 
		('delivery', 'Delivery Order')],
		string='Origin Control', readonly=False, 
		related='company_id.po_origin')