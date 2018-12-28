# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class DoubleCheck(models.TransientModel):

	_name = 'doublecheck.wizard'
	_description = 'Wizard: Asking the user to confirm changes when submitting forms.'

	# def _default_order(self):
	# 	return self.env['quality.order'].browse(self._context.get('active_id'))

	# order_id = fields.Many2one('quality.order', string='Order Reference', required=True, default=_default_order)

	text = fields.Char('Text')
