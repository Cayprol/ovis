# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class InheritProductTemplate(models.Model):
	
	_inherit = 'product.template'
	
	memo = fields.Text(string='Memorandum', translate=True)

	buyer_ids = fields.One2many('product.purchaserinfo', 'product_tmpl_id', string='Customers')	
	
	drawing = fields.Char(string='Drawaing', help="Engineer Drawing file name.")
	tooling_ids = fields.Many2many(comodel_name='product.template', relation='product_template_rel', column1='tooling_ids', column2='producing_ids', string="Tooling", ondelete='cascade', onupdate='cascade', readonly=True)
	producing_ids = fields.Many2many(comodel_name='product.template', relation='product_template_rel', column1='producing_ids', column2='tooling_ids', string="Producing", ondelete='cascade', onupdate='cascade')
	tooling = fields.Boolean(string='Is Tooling', index=True, default=False, required=True)

	arrival = fields.Date(string='Arrival Date', help="Arrival Date when this tooling comes in stock.")
	scrapped = fields.Boolean(string='Scrapped', default=False, help="This tooling product is scrapped.")
	exported = fields.Boolean(string='Exported', default=False, help="This tooling product is exported.")
	last_po = fields.Many2one('purchase.order', string='Last P/O', domain=[('state', '!=', 'draft')])
	last_so = fields.Many2one('sale.order', string='Last S/O', domain=[('state', '!=', 'draft')])

	@api.constrains('tooling', 'tooling_ids', 'producing_ids')
	def _check_tooling_producing(self):
		if len(self.producing_ids) > 0 and len(self.tooling_ids) > 0:
			raise ValidationError(_('Tooling and Producing do not co-exist.'))

		if self.tooling == True:
			if len(self.tooling_ids) > 0:
				raise ValidationError(_('A tooling product cannot have tooling.'))
			else:
				pass
			if len(self.producing_ids) <= 0:
				raise ValidationError(_('A tooling product must have at least one non-tooling product to produce.'))
			else:
				pass
		elif len(self.producing_ids) > 0:
				raise ValidationError(_('A non-tooling product cannot produce others.'))

	@api.multi
	@api.onchange('tooling')
	def reset_tooling_onchange(self):
		self.ensure_one()
		if self.tooling == False:
			self.scrapped = False
			self.exported = False

class PurchaserInfo(models.Model):
	_name = "product.purchaserinfo"
	_description = "Information about a product customer."
	_order = 'sequence, min_qty desc, price'
	
	name = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)], ondelete='cascade', required=True, help="Customer of this product")
	product_name = fields.Char('Customer Product Name',	help="This customer's product name will be used when printing a request for quotation. Keep empty to use the internal one.")
	product_code = fields.Char('Customer Product Code',	help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")
	sequence = fields.Integer('Sequence', default=1, help="Assigns the priority to the list of product customer.")
	product_uom = fields.Many2one('product.uom', 'Customer Unit of Measure', readonly=True, related='product_tmpl_id.uom_po_id', help="This comes from the product form.")
	min_qty = fields.Float('Minimal Quantity', default=0.0, required=True, help="The minimal quantity to sell to this customer, expressed in the customer Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
	price = fields.Float('Price', default=0.0, required=True, help="The price to sell a product to particular customer.")
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, index=1)
	currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id, required=True)
	date_start = fields.Date('Start Date', help="Start date for this customer price")
	date_end = fields.Date('End Date', help="End date for this customer price")
	product_id = fields.Many2one('product.product', 'Product Variant', help="If not set, the customer price will apply to all variants of this products.")
	product_tmpl_id = fields.Many2one('product.template', 'Product Template', index=True, ondelete='cascade', oldname='product_id')
	product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
	delay = fields.Integer('Delivery Lead Time', default=1, required=True, help="Lead time in days between the confirmation of the sales order and the products going out of your warehouse.")
	description = fields.Text(string='Description', help="Description regarding this Customer's pricing details.")


class InheritSupplierInfo(models.Model):
	_inherit = 'product.supplierinfo'

	sp_qty = fields.Float(string='Smallest Pack Quantity', help="Smallest Packing Quantity available from Vendor.")
	description = fields.Text(string='Description', help="Description regarding this Vendor's pricing details.")
