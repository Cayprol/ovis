# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _ 
import logging
_logger = logging.getLogger(__name__)

class ChangeOrder(models.Model):

	_name = 'change.order'
	_description = 'Change Order'

	@api.model
	def create(self, vals):
		if vals['parent_order_type'] == 'sale':
			vals['name'] = self.env['ir.sequence'].next_by_code('change.order.sale') or _('New')
		if vals['parent_order_type'] == 'purchase':
			vals['name'] = self.env['ir.sequence'].next_by_code('change.order.purchase') or _('New')

		return super(ChangeOrder, self).create(vals)

	name = fields.Char(string='Change Order', copy=False, readonly=True, index=True, default=lambda self: _('New'))
	parent_order_type = fields.Selection([('sale', 'Sales Order'), ('purchase', 'Purchase Order')], required=True, string='Parent Order Type')
	sale_order_id = fields.Many2one('sale.order', string='Sales Order', domain="[('state','=','sale')]")
	purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', domain="[('state','=','purchase')]")

	sale_order_line = fields.One2many(related='sale_order_id.order_line', string="Original Sales Order Lines")
	purchase_order_line = fields.One2many(related='purchase_order_id.order_line', string="Original Purchase Order Lines", readonly=False)

	description = fields.Text(string='Description', required=True, help='Word description for changing details and reasons.')

	approved_sale_order_line = fields.One2many('sale.order.line', 'approved_order_id', string='Approved Sales Order Lines') # copy=True, auto_join=True
	original_sale_order_line = fields.One2many('sale.order.line', 'original_order_id', string='Changed Sales Order Lines') # copy=True, auto_join=True

	partner_id = fields.Many2one(related='sale_order_id.partner_id', readonly=True)
	pricelist_id = fields.Many2one(related='sale_order_id.pricelist_id', readonly=True)
	company_id = fields.Many2one(related='sale_order_id.company_id', readonly=True)

	approver_id = fields.Many2one('res.users', string='Approver', readonly=True, track_visibility="onchange")
	executioner_id = fields.Many2one('res.users', string='Executioner', readonly=True, track_visibility="onchange")

	state = fields.Selection([
		('to approve', 'To Approve'),
		('approved', 'Approved'),
		('done', 'Done'),
		('cancel', 'Cancelled'),
	], string='Order Status', readonly=True, copy=False, default='to approve')

	@api.onchange('sale_order_id', 'purchase_order_id')
	def _onchange_parent_order_type(self):
		if self.sale_order_id:
			self.parent_order_type = 'sale'
		elif self.purchase_order_id:
			self.parent_order_type = 'purchase'
		else:
			self.parent_order_type = False

	@api.constrains('approver_id', 'create_uid')
	def _check_approver_id(self):
		for order in self:
			if self.env.user.has_group('base.group_no_one'):
				continue
			if order.approver_id == order.create_uid:
				raise exceptions.UserError(_("Cannot approve change order created by yourself."))

	def action_approve(self):
		self.write({
			'approver_id': self.env.user.id,
			'state': 'approved',
			})

	def action_cancel(self):
		self.write({
			'state': 'cancel',
			'approver_id': False,
			})

	def action_done(self):
		for order in self:
			for source_line in order.sale_order_line:
				source_line.update({
					'original_order_id': self.id,
					'order_id': False,
					})

			for approved_line in order.approved_sale_order_line:
				approved_line.update({
					'order_id': self.sale_order_id,
						})

			order.update({
				'state': 'done',
				'executioner_id': self.env.user.id,
				})

	def action_test(self):
		for order in self:
			_logger.warning("Order ID {}, sale_order_id {}, purchase_order_id {}".format(order.id, order.sale_order_id.id, order.purchase_order_id.id))
			# _logger.warning("purchase_order_id is False, result {}".format((order.purchase_order_id.id == False)))
			_logger.warning("purchase_order_id type is {}".format(type(order.purchase_order_id)))
			_logger.warning("parent_order_type is {}, type is {}".format(order.parent_order_type, type(order.parent_order_type)))