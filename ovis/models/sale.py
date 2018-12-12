# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class InheritSaleOrder(models.Model):

	_inherit = 'sale.order'

	ask_approve = fields.Date('Ask Approval Date', readonly=1, index=True, copy=False)
	date_approve = fields.Date('Approval Date', readonly=1, index=True, copy=False)
	state = fields.Selection([('draft', 'Quotation'),
							 ('to approve', 'To Approve'),
							 ('sent', 'Quotation Sent'),
							 ('sale', 'Sales Order'),
							 ('done', 'Locked'),
							 ('cancel', 'Cancelled'),],
							 string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')


	@api.multi
	def action_ask_approve(self, force=False):
		self.write({'state': 'to approve', 'ask_approve': fields.Date.context_today(self)})
		return {}
		
	@api.multi
	def action_approve(self, force=False):
		self.write({'state': 'sent', 'date_approve': fields.Date.context_today(self)})
		return {}
