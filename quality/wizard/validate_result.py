# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ValidateResult(models.TransientModel):

	_name = 'validate.result.wizard'
	_description = 'Wizard: Asking the user to confirm changes when submitting forms.'
	
	@api.multi
	def button_apply(self):
		record = self.env['quality.order'].browse(self._context.get('active_id'))
		record.ensure_one()
		record.write({'state': 'done',
					  'date_done': fields.datetime.now(),
					  'user_id': self.env.user.id})

		record.picking_id.purchase_id.action_view_invoice()


