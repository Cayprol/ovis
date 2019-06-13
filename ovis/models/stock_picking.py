# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class InheritPicking(models.Model):

	_inherit = 'stock.picking'

	forwarder_id = fields.Many2one('res.partner', 'Forwarder', help="Forwarder delevering the order.", domain="[('forwarder','=', True)]")

	def action_generate_backorder_wizard(self):
		view = self.env.ref('stock.view_backorder_confirmation')
		wiz = self.env['stock.backorder.confirmation'].create({'pick_ids': [(4, p.id) for p in self]})
		return {
			'name': _('Create Backorder?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.backorder.confirmation',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wiz.id,
			'context': {'parent_model': self._name,
						'parent_id': self.id},
		}

	def action_cancel_confirm(self):
		view = self.env.ref('ovis.view_cancel_confirmation')
		wiz = self.env['cancel.confirmation'].create({})
		return {
			'name': _('Confirm to Cancel?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'cancel.confirmation',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wiz.id,
			'context': {'parent_id': self.id,
						'parent_model': self._name},
		}

	# This method is designed for internal transfer from Quality Control to Stock, when partial movement is desired to go back to Input.
	def _reserve_to_input(self):
		_logger.info('_reserve_to_input called')
		warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', self.location_id.company_id.id)])
		_logger.info(warehouse_ids)
		for warehouse_id in warehouse_ids:
			if warehouse_id.lot_stock_id == self.location_dest_id and warehouse_id.wh_qc_stock_loc_id == self.location_id:
				input_location = warehouse_id.wh_input_stock_loc_id
				_logger.info(input_location)

		self.write({'location_dest_id': input_location.id})

