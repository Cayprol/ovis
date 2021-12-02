# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.tools import float_compare
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	is_blanket = fields.Boolean(related='order_id.is_blanket')
	# order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
	order_id = fields.Many2one('sale.order', string='Order Reference', required=False, ondelete='cascade', index=True, copy=False)

	@api.constrains('order_id')
	def _constrains_order_id(self):
		for record in self:
			if not record.order_id and not record.is_blanket:
				raise exceptions.ValidationError("order_id must not be null")

class BlanketOrderLine(models.Model):
	_name = 'blanket.order.line'
	_description = 'Blanket Order Line'
	_inherits = {'sale.order.line': 'sale_order_line_id'}
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', required=True, ondelete='cascade')
	blanket_order_id = fields.Many2one('blanket.order', string='Blanket Order Reference', required=True, ondelete='cascade', index=True, copy=False)
	state = fields.Selection(related='blanket_order_id.state', string='Order Status', copy=False, store=True)
	qty_to_sale = fields.Float('To Sale Qty', copy=False, digits='Product Unit of Measure', default=0.0, readonly=True, states={'open': [('readonly', False)]})
	qty_closed = fields.Float('Closed Qty', copy=False, digits='Product Unit of Measure', default=0.0, readonly=True)

	@api.onchange('product_id')
	def _onchange_product_description(self):
		description = self.product_id.description_sale or ""
		default_code = self.product_id.default_code or ""
		if default_code and description:
			self.name = default_code + '\n' + description
		elif not default_code and not description:
			self.name = self.product_id.name
		else:
			self.name = default_code or description

		self.product_uom = self.product_id.product_tmpl_id.uom_id

	@api.onchange('qty_to_sale')
	def _onchange_qty_to_sale(self):
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		if self.qty_to_sale < 0:
			self.qty_to_sale = 0
			return {
				'warning': {
					'title': _('Negative Quantity'),
					'message': _('To Sale Qty cannot be negative.'),
				}
			}
		if self.qty_to_sale > 0 and float_compare(self.qty_to_sale, self.product_uom_qty, precision_digits=precision) > 0:
			return {
				'warning': {
					'title': _('Over Quantity'),
					'message': _('To Sale Qty is more than the total quantity.'),
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
	@api.depends('blanket_order_id')
	def _get_order_id(self):
		for record in self:
			_logger.warning("the record blanket_order_id {} / its sale_order_id {}.".format(record.blanket_order_id, record.blanket_order_id.sale_order_id))
			record.order_id = record.blanket_order_id.sale_order_id

	@api.onchange('product_id')
	def _onchange_default_order_id(self):
		_logger.warning("the blanket_order_id {} and its sale_order_id is {}.".format(self.blanket_order_id, self.blanket_order_id.sale_order_id))
		self.order_id = self.blanket_order_id.sale_order_id

	def _compute_tax_id(self):
		for line in self:
			line = line.with_company(line.company_id)
			fpos = line.blanket_order_id.fiscal_position_id or line.blanket_order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
			# If company_id is set, always filter taxes by the company
			taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
			line.tax_id = fpos.map_tax(taxes)
