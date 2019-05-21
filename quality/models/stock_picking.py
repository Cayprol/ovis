from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError
# from odoo.addons import decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class InheritPicking(models.Model):

	_inherit = 'stock.picking'

	@api.multi
	def _prepare_quality_order_line(self, quality_order_id):
		self.ensure_one()

		order_lines = []
		if self.move_ids_without_package:
			for move in self.move_ids_without_package:
				order_lines.append((0, 0, {'product_id': move.product_id.id,
											'product_qty': move.product_qty,
				 					 		'product_uom': move.product_uom.id,
				 					 		'order_id': quality_order_id}))

		return order_lines

	@api.multi
	def action_done(self):
		super(InheritPicking, self).action_done()

		# Create new record in model 'quality.order'
		quality_order = self.env['quality.order'].create({'origin': self.name,
														  'company_id': self.company_id.id,
														  'user_id': self.env.uid,
														  'date': fields.Datetime.now(),
														  'picking_id': self.id})
		# Format a list of new records for One2many field 'order_line' in model 'quality.oder' which relates to child model 'quality.order.line'.
		# quality_order.id is the newly created record id, so all 'quality.order.line' will be linked back to this 'quality.order' record.
		order_lines = self._prepare_quality_order_line(quality_order.id)
		quality_order.write({'order_line': order_lines}) 

		to_do = self.env['mail.activity'].create({'activity_type_id': 4,
												  'res_id': quality_order.id,
												  'res_model_id': self.env['ir.model'].search([('model', '=', self.env['quality.order']._name)]).id,
												  'date_deadline': datetime.today()+relativedelta(days=+self.company_id.qo_lead),
												  'user_id': self.env.user.id,
												  'summary': _('Auto-generated for {}.'.format(self.name)),
												  'note': _('This quality order is auto-generated for {}.\nPlease validate all information and finish inspection ASAP.'.format(self.name))})

		return True
