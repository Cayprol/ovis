# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


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
			'context': {'parent_id': self.id,
						'parent_model': self._name},
		}




