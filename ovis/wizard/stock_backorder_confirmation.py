# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools.float_utils import float_compare

import logging
_logger = logging.getLogger(__name__)

class StockBackorderConfirmation(models.TransientModel):

	_inherit = 'stock.backorder.confirmation'

	def process(self):
		super(StockBackorderConfirmation, self).process()
		stock_picking = self.env[self._context['parent_model']].browse(self._context['parent_id'])
		backorder_created = self.env['stock.picking'].search([('backorder_id', '=', stock_picking.id)])
		_logger.info("Picking: {} - Backorder: {}".format(stock_picking, backorder_created))
		note = _('Follow up on {} & {}'.format(stock_picking.name, backorder_created.name))
		
		# Notify Purchaser
		po = stock_picking.purchase_id
		procurement_group = stock_picking.group_id
		if procurement_group:
			po = self.env['purchase.order'].search([('group_id.id','=',procurement_group.id)])
			_logger.info("{} associated with {}. Length of ID list: {}".format(procurement_group ,po, len(po)))
			for p in po:
				# msg = _('%s generates backorder %s') % (stock_picking.name, backorder_created.name)
				msg = _('{} generates backorder {}'.format(stock_picking.name, backorder_created.name))
				p.message_post(body=msg)
				p.activity_schedule('mail.mail_activity_data_todo', 
									date_deadline=datetime.today(), 
									summary='Backorder Created', 
									note=note)

		# Variables for Notify Owner
		else:
			dest_owner = stock_picking.location_dest_id.partner_id
			dest_owner_in_res_users = self.env['res.users'].search([('name','=',dest_owner.name)])
			if dest_owner and dest_owner.company_type == 'person':
				stock_picking.activity_schedule('mail.mail_activity_data_todo', date_deadline=datetime.today(), summary='Backorder Created', note=note)

			else:
				_logger.info("No Purchase Order or Location Owner Found, No one is explicitly notified by Planned Activity.")




	def action_reject(self):
		for pick_id in self.pick_ids:
			_logger.info("The 'stock.picking' record generating this log is {}".format(pick_id))
			moves_to_log = {}
			for move in pick_id.move_lines:
				if float_compare(move.product_uom_qty, move.quantity_done, precision_rounding=move.product_uom.rounding) > 0:
					moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
					_logger.info("float_compare returned > 0 True, moves_to_log = {}".format(moves_to_log))
			pick_id._log_less_quantities_than_expected(moves_to_log)
 # float_compare returned > 0 True, moves_to_log = {stock.move(14,): (2.0, 3.0)}
		self.pick_ids.action_done()
		for pick_id in self.pick_ids:
			backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
			backorder_pick._reserve_to_input()
			pick_id.message_post(body=_("Returning <em>%s</em> to <b>Input</b>.") % (backorder_pick.name))