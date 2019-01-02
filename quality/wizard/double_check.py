# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DoubleCheck(models.TransientModel):

	_name = 'doublecheck.wizard'
	_description = 'Wizard: Asking the user to confirm changes when submitting forms.'

	# def _default_order(self):
	# 	return self.env['quality.order'].browse(self._context.get('active_id'))

	# order_id = fields.Many2one('quality.order', string='Order Reference', required=True, default=_default_order)
	
	@api.multi
	def button_apply(self):
		record = self.env['quality.order'].browse(self._context.get('active_id'))
		if record.button_validate():
			return True
		else:
			raise ValidationError(_('The order is not in waiting state to be validated.'))