# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	is_blanket = fields.Boolean(string='Is blanket', readonly=True, help='Technical field to filter out blanket orders from sale order views due to delegation inheritance.')
	blanket_order_id = fields.Many2one('blanket.order', string='Blanket Order', readonly=True, help='Technical field to track which blanket order this sale order is created from.')

class BlanketOrder(models.Model):
	_name = 'blanket.order'
	_description = 'Blanket Order'
	_inherits = {'sale.order': 'sale_order_id'}
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
	blanket_order_line = fields.One2many('blanket.order.line', 'blanket_order_id', string='Blanket Order Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('open', 'Open'),
		('closed', 'Closed'),
		('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
	sale_order_ids = fields.One2many('sale.order', 'blanket_order_id', readonly=True, help='Sales Order created from this blanket order.')
	sale_count = fields.Integer(string='Sales Count', compute='_get_sales')

	@api.onchange('fiscal_position_id')
	def _compute_tax_id(self):
		"""
		Trigger the recompute of the taxes if the fiscal position is changed on the BO.
		"""
		for order in self:
			# order.order_line._compute_tax_id()
			order.blanket_order_line._compute_tax_id()

	@api.onchange('expected_date')
	def _onchange_expected_date(self):
		self.commitment_date = self.expected_date

	@api.onchange('partner_shipping_id', 'partner_id', 'company_id')
	def onchange_partner_shipping_id(self):
		"""
		Trigger the change of fiscal position when the shipping address is modified.
		"""
		self.fiscal_position_id = self.env['account.fiscal.position'].with_company(self.company_id).get_fiscal_position(self.partner_id.id, self.partner_shipping_id.id)
		return {}

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		"""
		Update the following fields when the partner is changed:
		- Pricelist
		- Payment terms
		- Invoice address
		- Delivery address
		- Sales Team
		"""
		if not self.partner_id:
			self.update({
				'partner_invoice_id': False,
				'partner_shipping_id': False,
				'fiscal_position_id': False,
			})
			return

		self = self.with_company(self.company_id)

		addr = self.partner_id.address_get(['delivery', 'invoice'])
		partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
		values = {
			'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
			'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
			'partner_invoice_id': addr['invoice'],
			'partner_shipping_id': addr['delivery'],
		}
		user_id = partner_user.id
		if not self.env.context.get('not_self_saleperson'):
			user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
		if user_id and self.user_id.id != user_id:
			values['user_id'] = user_id

		if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms'):
			if self.terms_type == 'html' and self.env.company.invoice_terms_html:
				baseurl = html_keep_url(self.get_base_url() + '/terms')
				values['note'] = _('Terms & Conditions: %s', baseurl)
			elif not is_html_empty(self.env.company.invoice_terms):
				values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
		if not self.env.context.get('not_self_saleperson') or not self.team_id:
			values['team_id'] = self.env['crm.team'].with_context(
				default_team_id=self.partner_id.team_id.id
			)._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
		self.update(values)

	@api.onchange('user_id')
	def onchange_user_id(self):
		if self.user_id:
			self.team_id = self.env['crm.team'].with_context(
				default_team_id=self.team_id.id
			)._get_default_team_id(user_id=self.user_id.id, domain=None)

	@api.onchange('partner_id')
	def _onchange_partner_id_warning(self):
		if not self.partner_id:
			return
		partner = self.partner_id

		# If partner has no warning, check its company
		if partner.sale_warn == 'no-message' and partner.parent_id:
			partner = partner.parent_id

		if partner.sale_warn and partner.sale_warn != 'no-message':
			# Block if partner only has warning but parent company is blocked
			if partner.sale_warn != 'block' and partner.parent_id and partner.parent_id.sale_warn == 'block':
				partner = partner.parent_id

			if partner.sale_warn == 'block':
				self.update({'partner_id': False, 'partner_invoice_id': False, 'partner_shipping_id': False, 'pricelist_id': False})

			return {
				'warning': {
					'title': _("Warning for %s", partner.name),
					'message': partner.sale_warn_msg,
				}
			}

	@api.onchange('commitment_date')
	def _onchange_commitment_date(self):
		""" Warn if the commitment dates is sooner than the expected date """
		if (self.commitment_date and self.expected_date and self.commitment_date < self.expected_date):
			return {
				'warning': {
					'title': _('Requested date is too soon.'),
					'message': _("The delivery date is sooner than the expected date."
								 "You may be unable to honor the delivery date.")
				}
			}

	@api.onchange('pricelist_id', 'blanket_order_line')
	def _onchange_pricelist_id(self):
		if self.blanket_order_line and self.pricelist_id and self._origin.pricelist_id != self.pricelist_id:
			self.show_update_pricelist = True
		else:
			self.show_update_pricelist = False


	@api.model
	def create(self, vals):
		if 'company_id' in vals:
			self = self.with_company(vals['company_id'])
		if vals.get('name', _('New')) == _('New'):
			seq_date = None
			if 'date_order' in vals:
				seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
			vals['name'] = self.env['ir.sequence'].next_by_code('blanket.order', sequence_date=seq_date) or _('New')

		# Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
		if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			addr = partner.address_get(['delivery', 'invoice'])
			vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
			vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
			vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)
		vals['is_blanket'] = True
		result = super(BlanketOrder, self).create(vals)
		return result

	@api.depends('sale_order_ids')
	def _get_sales(self):
		for record in self:
			record.sale_count = len(record.sale_order_ids)

	def action_sale(self):
		self.ensure_one()
		if self.state != 'open':
			raise exceptions.UserError(_("Only open blanket orders can be converted to sale orders."))

		new_sale_order = self.sale_order_id.copy({'is_blanket': False, 'blanket_order_id': self.id})
		for bol, sol in zip(self.blanket_order_line, self.blanket_order_line.sale_order_line_id):
			new_sol = sol.copy({
				'is_blanket': False, 
				'order_id': new_sale_order.id, 
				'product_uom_qty': bol.qty_to_sale})
			bol.qty_closed += bol.qty_to_sale
			bol.qty_to_sale = 0
		new_sale_order.action_confirm()
		return {
				'type': 'ir.actions.act_window',
				'res_model': 'sale.order',
				'res_id': new_sale_order.id,
				'views': [(self.env.ref('sale.view_order_form').id, 'form')],
			}

	def action_open(self):
		for status in set(self.mapped('state')):
			if status != 'draft':
				raise exceptions.UserError(_("Only draft blanket orders are allowed to be opened."))
		return self.write({'state': 'open'})

	def action_cancel(self):
		for status in set(self.mapped('state')):
			if status != 'open':
				raise exceptions.UserError(_("Only open blanket orders are allowed to be cancelled."))
		return self.write({'state': 'cancel'})

	def update_prices(self):
		self.ensure_one()
		lines_to_update = []
		for line in self.order_line.filtered(lambda line: not line.display_type):
			product = line.product_id.with_context(
				partner=self.partner_id,
				quantity=line.product_uom_qty,
				date=self.date_order,
				pricelist=self.pricelist_id.id,
				uom=line.product_uom.id
			)
			price_unit = self.env['account.tax']._fix_tax_included_price_company(
				line._get_display_price(product), line.product_id.taxes_id, line.tax_id, line.company_id)
			if self.pricelist_id.discount_policy == 'without_discount' and price_unit:
				discount = max(0, (price_unit - product.price) * 100 / price_unit)
			else:
				discount = 0
			lines_to_update.append((1, line.id, {'price_unit': price_unit, 'discount': discount}))
		self.update({'order_line': lines_to_update})
		self.show_update_pricelist = False
		self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", self.pricelist_id.display_name))

	def action_view_sale(self):
		return {
			'name': _('Sales Orders'),
			'type': 'ir.actions.act_window',
			'res_model': 'sale.order',
			'views': [(self.env.ref('sale.view_order_tree').id, 'tree')],
			'domain': [('blanket_order_id', '=', self.id)],
			}