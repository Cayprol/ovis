from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError
# from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class InheritPicking(models.Model):

	_inherit = 'stock.picking'

	@api.multi
	def _prepare_quality_order_line(self):
		self.ensure_one()

		order_lines = []
		if self.move_ids_without_package:
			for move in self.move_ids_without_package:
				order_lines.append((0, 0, {'product_id': move.product_id.id,
				 					'product_qty': move.product_qty,
				 					'product_uom': move.product_uom.id,
				 					'order_id': self.id}))

		return order_lines

	@api.multi
	def action_done(self):
		super(InheritPicking, self).action_done()

		order_lines = self._prepare_quality_order_line()
		quality_order = self.env['quality.order'].create({'origin': self.name,
														  'company_id': self.company_id.id,
														  'date': fields.Datetime.now(),
														  'picking_id': self.id,
														  'order_line': order_lines})
		to_do = self.env['mail.activity'].create({'activity_type_id': 4,
												  'res_id': quality_order.id,
												  'res_model_id': self.env['ir.model'].search([('model', '=', self.env['quality.order']._name)]).id,
												  'date_deadline': fields.Date.today(),
												  'user_id': self.env.user.id,
												  'summary': _('Auto-generated for {}.'.format(self.name)),
												  'note': _('This quality order is auto-generated for {}.\nPlease validate all information and finish inspection ASAP.'.format(self.name))})

		return True
