# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

class ChangeSaleOrder(models.Model):

	_name = 'change.sale.order'
	_description = 'Change Sale Order'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	READONLY_STATES = {
		'approved': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('change.sale.order') or _('New')

		record = super(ChangeSaleOrder, self).create(vals)

		approver_id_partner_id = record.approver_id.partner_id
		if approver_id_partner_id:
			record.message_subscribe(partner_ids=[approver_id_partner_id.id])
			deadline = fields.Date.context_today(self) + timedelta(days=3)
			summary = _("Approve this order")
			record.activity_schedule(user_id=record.approver_id.id, act_type_xmlid='mail.mail_activity_data_todo', date_deadline=deadline, summary=summary)

		return record

	def write(self, vals):
		"""
		When changing the approver, unsub the old approver from the record, and sub the new approver to record.
		"""
		approver_id = vals.get('approver_id')
		if approver_id:
			current_approver_id_partner_id = self.approver_id.partner_id.id or None
			new_approver_id_partner_id = self.env['res.users'].browse(approver_id).partner_id.id or None
			self.message_unsubscribe(partner_ids=[current_approver_id_partner_id])
			self.message_subscribe(partner_ids=[new_approver_id_partner_id])

		return super(ChangeSaleOrder, self).write(vals)

	name = fields.Char(string='Change Order', copy=False, readonly=True, index=True, default=lambda self: _('New'))
	sale_order_id = fields.Many2one('sale.order', string='Sales Order', domain="[('state','=','sale')]", required=True, states={'to approve': [('readonly', False)], 'approved': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
	sale_order_line = fields.One2many(related='sale_order_id.order_line', readonly=True, string="Sales Order Lines")

	description = fields.Text(string='Description', required=True, states=READONLY_STATES, help='Word description for changing details and reasons.')

	approved_sale_order_line = fields.One2many('sale.order.line', 'approved_order_id', states=READONLY_STATES, string='Approved Sales Order Lines') # copy=True, auto_join=True
	original_sale_order_line = fields.One2many('sale.order.line', 'original_order_id', readonly=True, string='Original Sales Order Lines') # copy=True, auto_join=True

	partner_id = fields.Many2one(related='sale_order_id.partner_id', readonly=True)
	pricelist_id = fields.Many2one(related='sale_order_id.pricelist_id', readonly=True)
	company_id = fields.Many2one(related='sale_order_id.company_id', readonly=True)

	approver_id = fields.Many2one('res.users', string='Approver', states=READONLY_STATES, required=True, track_visibility="onchange", ondelete="RESTRICT")
	executioner_id = fields.Many2one('res.users', string='Executioner', readonly=True, track_visibility="onchange", ondelete="RESTRICT")

	currency_id = fields.Many2one("res.currency", related='sale_order_id.currency_id', string="Currency", readonly=True, required=True)

	original_amount_untaxed = fields.Monetary(string='Original Untaxed Amount', store=True, readonly=True, compute='_original_amount_all', tracking=5)
	original_amount_tax = fields.Monetary(string='Original Taxes', store=True, readonly=True, compute='_original_amount_all')
	original_amount_total = fields.Monetary(string='Original Total', store=True, readonly=True, compute='_original_amount_all', tracking=4)

	changed_amount_untaxed = fields.Monetary(string='Changed Untaxed Amount', store=True, readonly=True, compute='_changed_amount_all', tracking=5)
	changed_amount_tax = fields.Monetary(string='Changed Taxes', store=True, readonly=True, compute='_changed_amount_all')
	changed_amount_total = fields.Monetary(string='Changed Total', store=True, readonly=True, compute='_changed_amount_all', tracking=4)

	state = fields.Selection([
		('to approve', 'To Approve'),
		('approved', 'Approved'),
		('done', 'Done'),
		('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, default='to approve', tracking=True)

	@api.constrains('approver_id', 'create_uid')
	def _check_approver_id(self):
		for order in self:
			# The superuser is uid==1, the user for testing and developing purpose is uid==2 which was created by Odoo through Web UI database creation
			if self.env.uid==2:
				continue
			if order.approver_id == order.create_uid:
				raise exceptions.UserError(_("Cannot approve change order created by yourself."))
			if order.state in ('done') and not order.executioner_id:
				raise exceptions.ValidationError(_("Done state must have an executioner."))

	def action_approve(self):
		for order in self:
			if self.env.user.has_group('sales_team.group_sale_manager'):
				order.update({
					'approver_id': self.env.user.id,
					'state': 'approved',
				})
				# By design, a res.users record creates a res.partner record on creation, 
				# but if some LDAP or external Login modules bugged, res.users may not have corresponding partner_id
				if self.env.user.partner_id:
					order.sale_order_id.message_subscribe(partner_ids=[self.env.user.partner_id.id])

			else:
				raise exceptions.UserError(_("Cannot approve {name}. Must be a manager to approve change orders.".format(name=order.name)))


	def action_cancel(self):
		if 'done' in self.mapped('state'):
			raise exceptions.UserError(_("Change order in state Done cannot be canceled."))
		self.write({
			'state': 'cancel',
			})

	def action_done(self):
		for order in self:
			for source_line in order.sale_order_line:
				moves = self.env['stock.move'].search([('sale_line_id','=',source_line.id),('state','not in',['cancel','done'])])
				moves._do_unreserve()
				moves._clean_merged()
				moves._action_cancel()
				source_line.update({
					'original_order_id': order.id,
					'order_id': False,
					'qty_delivered_manual': source_line.qty_delivered,
					})

			for approved_line in order.approved_sale_order_line:
				approved_line.update({
					'order_id': order.sale_order_id,
						})

			order.sale_order_id.action_confirm()

			order.update({
				'state': 'done',
				'executioner_id': self.env.user.id,
				})
			# The placeholder name and .format() must be in this particular format for the translation to work.
			thread_msg = _("Changed order <b>{name}</b> has been executed.").format(name=order.name)
			order.sale_order_id.message_post(body=thread_msg)
			if self.env.user.partner_id:
				order.sale_order_id.message_subscribe(partner_ids=[self.env.user.partner_id.id])
				order.message_subscribe(partner_ids=[self.env.user.partner_id.id])

	def _track_subtype(self, init_values):
		self.ensure_one()
		if 'state' in init_values and self.state == 'done':
			return self.env.ref('change_order.mt_change_executed')

		return super(ChangeSaleOrder, self)._track_subtype(init_values)

	@api.depends('approved_sale_order_line.price_total')
	def _changed_amount_all(self):
		"""
		Compute the total changed amounts of the Change Order.
		"""
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.approved_sale_order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			order.update({
				'changed_amount_untaxed': amount_untaxed,
				'changed_amount_tax': amount_tax,
				'changed_amount_total': amount_untaxed + amount_tax,
			})

	@api.depends('original_sale_order_line.price_total')
	def _original_amount_all(self):
		"""
		Compute the total original amounts of the Change Order.
		"""
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.original_sale_order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			order.update({
				'original_amount_untaxed': amount_untaxed,
				'original_amount_tax': amount_tax,
				'original_amount_total': amount_untaxed + amount_tax,
			})