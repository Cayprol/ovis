# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	invoice_policy_forced = fields.Selection(string='Invoicing Policy Forced', readonly=False, related='company_id.invoice_policy_forced')

	force_invoice_policy = fields.Boolean('Force Policy', readonly=False, related='company_id.force_invoice_policy')