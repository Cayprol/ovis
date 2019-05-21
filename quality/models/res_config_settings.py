# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	adjust_qo_lead = fields.Boolean(string='Default Order Lead', config_parameter='quality.adjust_qo_lead')
	qo_lead = fields.Integer(related='company_id.qo_lead', string='Days To Deadline', readonly=False)

	@api.onchange('adjust_qo_lead')
	def _onchange_adjust_qo_lead(self):
		if self.qo_lead < 0:
			# self.qo_lead = self.env['res.company'].default_get(['qo_lead'])['qo_lead']
			return {
                'warning': {'title': "Warning", 'message': "Quality Order Lead Time must be greater than or equal to 0."},
			}