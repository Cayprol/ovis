# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	default_invoice_policy = fields.Selection([
		('order', 'Invoice what is ordered'),
		('delivery', 'Invoice what is delivered')
		], 'Invoicing Policy',
		readonly=False,
		related='company_id.default_invoice_policy')

	force_invoice_policy = fields.Boolean('Force Policy', readonly=False, related='company_id.force_invoice_policy')