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
		order_lines = {}
		if self.move_ids_without_package:
			for move in self.move_ids_without_package:
				order_lines['product_id'] = move.product_id.id
				order_lines['product_qty'] = move.product_qty
				order_lines['product_uom'] = move.product_uom.id
				order_lines['order_id'] = self.id

		return order_lines


	@api.multi
	def action_done(self):
		super(InheritPicking, self).action_done()

		order_lines = self._prepare_quality_order_line()
		quality_order = self.env['quality.order'].create({'origin': self.name,
														  'company_id': self.company_id.id,
														  'date': fields.Datetime.now(),
														  'picking_id': self.id,
														  'order_line': [(0, 0, order_lines)]})

		return quality_order
