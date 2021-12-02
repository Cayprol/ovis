# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.tools import float_compare
import logging
_logger = logging.getLogger(__name__)
class BlanketOrderLine(models.Model):
	_name = 'blanket.order.line'
	_description = 'Blanket Order Lines'
	_check_company_auto = True

	@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		"""
		Compute the amounts of the BO line.
		"""
		for line in self:
			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			taxes = line.tax_id.compute_all(price, line.blanket_order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.blanket_order_id.partner_id)
			line.update({
				'price_tax': taxes['total_included'] - taxes['total_excluded'],
				'price_total': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
			})
			if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
				line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

	@api.depends('product_id', 'blanket_order_id.state', 'qty_converted')
	def _compute_product_updatable(self):
		for line in self:
			if line.state in ['closed', 'cancel'] or (line.state == 'open' and line.qty_converted > 0):
				line.product_updatable = False
			else:
				line.product_updatable = True

	@api.depends('state')
	def _compute_product_uom_readonly(self):
		for line in self:
			line.product_uom_readonly = line.state in ['open', 'closed', 'cancel']

	@api.onchange('product_id')
	def _onchange_product_description(self):
		des = {'sale': self.product_id.description_sale, 'purchase': self.product_id.description_purchase}
		description = des.get(self.order_type) or ""
		default_code = self.product_id.default_code or ""
		if default_code and description:
			self.name = default_code + '\n' + description
		elif not default_code and not description:
			self.name = self.product_id.name
		else:
			self.name = default_code or description

		self.product_uom = self.product_id.product_tmpl_id.uom_id

	@api.onchange('qty_to_convert')
	def _onchange_qty_to_convert(self):
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		if self.qty_to_convert < 0:
			self.qty_to_convert = 0
			return {
				'warning': {
					'title': _('Negative Quantity'),
					'message': _('To Convert quantity cannot be negative.'),
				}
			}
		if self.qty_to_convert > 0 and float_compare(self.qty_to_convert, self.product_uom_qty, precision_digits=precision) > 0:
			return {
				'warning': {
					'title': _('Over Quantity'),
					'message': _('To Convert quantity is more than the total quantity.'),
				}
			}

	@api.onchange('product_uom_qty')
	def _onchange_product_uom_qty(self):
		if self.product_uom_qty < 0:
			self.product_uom_qty = 0
			return {
				'warning': {
					'title': _('Negative Quantity'),
					'message': _('Quantity cannot be negative.'),
				}
			}

	@api.onchange('price_unit')
	def _onchange_product_uom_qty(self):
		if self.price_unit < 0:
			self.price_unit = 0
			return {
				'warning': {
					'title': _('Negative Quantity'),
					'message': _('Unit Price cannot be negative.'),
				}
			}

	@api.constrains('product_uom_qty', 'qty_converted', 'qty_to_convert', 'price_unit')
	def _constrains_no_negative(self):
		# This method is a just-in-case protection to verify non-negative numeric fields
		# Define onchange method for all non-negative numeric fields to reflect constaints to UI
		for record in self:
			is_negative = {
				record.product_uom_qty < 0: self._fields['product_uom_qty'].string,
				record.qty_converted < 0: self._fields['qty_converted'].string,
				record.qty_to_convert < 0: self._fields['qty_to_convert'].string,
				record.price_unit < 0: self._fields['price_unit'].string,
			}
			if is_negative.get(True):
				raise exceptions.ValidationError(_('{field_name} cannot be negative.'.format(field_name=is_negative.get(True))))

	blanket_order_id = fields.Many2one('blanket.order', string='Blanket Order Reference', required=True, ondelete='cascade', index=True, copy=False)
	name = fields.Text(string='Description', required=True)
	sequence = fields.Integer(string='Sequence', default=10)
	price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
	price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
	price_tax = fields.Float(compute='_compute_amount', string='Total Tax', store=True)
	price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)

	tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
	
	discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

	product_id = fields.Many2one(
		'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
		change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
	product_template_id = fields.Many2one(
		'product.template', string='Product Template',
		related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])
	product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', default=True)
	product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
	product_uom = fields.Many2one('uom.uom', 
		string='Unit of Measure', ondelete="restrict",
		domain="[('category_id', '=', product_uom_category_id)]", default=lambda self: self.env.context.get('uom') or self.product_id.uom_id.id)
	product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
	product_uom_readonly = fields.Boolean(compute='_compute_product_uom_readonly')

	currency_id = fields.Many2one(related='blanket_order_id.currency_id', depends=['blanket_order_id.currency_id'], store=True, string='Currency')
	company_id = fields.Many2one(related='blanket_order_id.company_id', string='Company', store=True, index=True)
	order_partner_id = fields.Many2one(related='blanket_order_id.partner_id', store=True, string='Customer')

	qty_to_convert = fields.Float('To Convert Quantity', copy=False, digits='Product Unit of Measure', default=0.0)
	qty_converted = fields.Float('Converted Quantity', readonly=True, copy=False, digits='Product Unit of Measure', default=0.0)

	state = fields.Selection(
		related='blanket_order_id.state', string='Order Status', copy=False, store=True)
	order_type = fields.Selection(
		related='blanket_order_id.order_type', string='Order Type', copy=False, store=True)

	display_type = fields.Selection([
		('line_section', "Section"),
		('line_note', "Note")], default=False, help="Technical field for UX purpose.")