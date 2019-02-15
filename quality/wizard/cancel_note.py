# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class CancelNote(models.TransientModel):

	_name = 'cancelnote.wizard'
	_description = 'Wizard: Asking the user to commit note when canceling order.'

	note = fields.Text('Notes')
	
	@api.multi
	def button_apply(self):
		record = self.env['quality.order'].browse(self._context.get('active_id'))
		record.ensure_one()
		if record.note != False:
			record.write({'note': record.note + "\nCanceled because: " + self.note,
						  'state': 'cancel'})
		else:
			record.write({'note': "Canceled because: " + self.note,
						  'state': 'cancel'})

