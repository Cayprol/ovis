# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

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
		actions = [line.action for line in record.order_line]
		
		if 'pending' in actions:
			raise UserError(_('There are pending items left.'))

		elif 'reject' in actions:
			source_po = record.picking_id.purchase_id
			if source_po:
				to_do = self.env['mail.activity'].create({'activity_type_id': 4,
												  'res_id': source_po.id,
												  'res_model_id': self.env['ir.model'].search([('model', '=', self.env['purchase.order']._name)]).id,
												  'date_deadline': datetime.now()+relativedelta(days=+1),
												  'user_id': source_po.user_id.id,
												  'summary': _('Auto-generated for {}.'.format(record.name)),
												  'note': _('{}, related to this PO, failed our quality standard.\n'.format(record.name))})

		# This Line of condition needsd to be re-write.
		elif len(set(actions)) == 1 and 'qualify' in actions:
			_logger.info('All actions are Qualify.  Ready to invoice.')

