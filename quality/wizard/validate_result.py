# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class ValidateResult(models.TransientModel):

	_name = 'validate.result.wizard'
	_description = 'Wizard: Warn users at least one line in the order has unmatched quantity of "Quantity" and "Qty Done".'
	
	@api.multi
	def button_apply(self):
		order = self.env['quality.order'].browse(self._context.get('active_id'))
		order.ensure_one()

		order.write({'state': 'done',
					  'date_done': fields.datetime.now(),
					  'user_id': self.env.user.id})

		source_po = order.picking_id.purchase_id
		if source_po:
			self.env['mail.activity'].create({'activity_type_id': 4,
											  'res_id': source_po.id,
											  'res_model_id': self.env['ir.model'].search([('model', '=', self.env['purchase.order']._name)]).id,
											  'date_deadline': datetime.today(),
											  'user_id': source_po.user_id.id,
											  'summary': _('Auto-generated for {}.'.format(order.name)),
											  'note': _('Quality Order {} related to Purchase Order {} requires further attention.\n'.format(order.name, source_po.name))})

