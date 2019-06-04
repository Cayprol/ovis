# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class StockBackorderConfirmation(models.TransientModel):

	_inherit = 'stock.backorder.confirmation'

	def process(self):
		super(StockBackorderConfirmation, self).process()
		
		stock_picking = self.env['stock.picking'].browse(self._context['parent_id'])
		backorder_created = self.env['stock.picking'].search([('backorder_id', '=', stock_picking.id)])
		_logger.info("Picking: {} - Backorder: {}".format(stock_picking, backorder_created))

		# Variables for Notify Owner
		dest_owner = stock_picking.location_dest_id.partner_id
		dest_owner_in_res_users = self.env['res.users'].search([('name','=',dest_owner.name)])
		# # # # #

		# Notify Purchaser
		po = stock_picking.purchase_id
		procurement_group = stock_picking.group_id
		if procurement_group:
			po = self.env['purchase.order'].search([('group_id.id','=',procurement_group.id)])
			_logger.info("The stock.picking record belongs to a procurement group associated with {}. Length of ID list: {}".format(po, len(po)))
			
			for p in po:
				self.env['mail.activity'].create({'activity_type_id': 4,
											  'res_id': p.id,
											  'res_model_id': self.env['ir.model'].search([('model', '=', p._name)]).id,
											  'date_deadline': datetime.today(),
											  'user_id': p.user_id.id,
											  'summary': _('Backorder Created'),
											  'note': _('Backorder {} associated with {} was created.'.format(backorder_created.name, stock_picking.name))})

		elif dest_owner and dest_owner.company_type == 'person':
			self.env['mail.activity'].create({'activity_type_id': 4,
								  			  'res_id': stock_picking.id,
								  			  'res_model_id': self.env['ir.model'].search([('model', '=', stock_picking._name)]).id,
											  'date_deadline': datetime.today(),
											  'user_id': dest_owner_in_res_users.id,
											  'summary': _('Backorder Created'),
											  'note': _('Backorder {} associated with {} was created.'.format(backorder_created.name, stock_picking.name))})

		else:
			_logger.info("No Purchase Order or Location Owner Found, No one is explicitly notified by Planned Activity.")
