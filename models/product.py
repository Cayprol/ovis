# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError

class InheritProductTemplate(models.Model):
	
	_inherit = 'product.template'
	_parent_name = "parent_id"
	_parent_store = True
	_parent_order = 'name'
	drawing = fields.Char(string='Drawaing', help="Engineer Drawing file name.")

	# molding_id = fields.One2many('product.molding', 'product_molding_id', string="Molding", help="Molding & Tooling information of the product.")
	tooling = fields.Boolean(string='Is tooling', index=True, default=False)
	parent_id = fields.Many2one('product.template', string='Parent', index=True, ondelete='cascade')
	child_ids = fields.One2many('product.template', 'parent_id', string='Old Versions')	
	parent_left = fields.Integer('Left Parent', index=1)
	parent_right = fields.Integer('Right Parent', index=1)
	@api.constrains('parent_id')
	def _check_parent_id(self):
		if not self._check_recursion():
			raise exceptions.ValidationError('Error ! You can not create recursive tags.')

	buyer_ids = fields.One2many('product.purchaserinfo', 'product_tmpl_id', string='Customers')	


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

class InheritSupplierInfo(models.Model):
	_inherit = 'product.supplierinfo'

	sp_qty = fields.Float(string='Smallest Pack Quantity', help="Smallest Packing Quantity available from Vendor.")
	info = fields.Text(string='Additional Information', help="Additional Information regarding this Vendor's pricing details.")
	
	# Use xml attribute "decoration-danger" for coherence of code.
	# @api.multi
	# @api.constrains('sp_qty', 'min_qty')
	# def _check_qty(self):
	# 	self.ensure_one()
	# 	if self.sp_qty > self.min_qty:
	# 		raise exceptions.ValidationError("Smallest Packing Quantity must be smaller than or equal to Minimal Quantity.")


# custom class for tooling if it is NOT a product, BUT instead being a separate entity. 
# class ProductMolding(models.Model):
# 	_name = 'product.molding'
# 	_parent_name = "parent_id"
# 	_parent_store = True
# 	_parent_order = 'name'
# 	_rec_name = 'name'

# 	product_molding_id = fields.Many2one('product.template', 'molding')

# 	name = fields.Char(string='Molding Name', required=True, translate=True)
# 	customer_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)], ondelete='cascade', help="Customer of this Molding.")
# 	vendor_id = fields.Many2one('res.partner', 'Vendor', domain=[('supplier', '=', True)], ondelete='cascade', help="Vendor of this Molding.")
# 	arrival = fields.Date(string='Arrival Date', help="Date when this molding comes in stock.")
# 	price = fields.Float('Price', default=0.0, required=True, help="The price of this molding.")
# 	currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id, required=True)

# 	parent_id = fields.Many2one('product.molding', string='Related Molding', index=True, ondelete='cascade')
# 	child_ids = fields.One2many('product.molding', 'parent_id', string='Old Versions')
# 	parent_left = fields.Integer('Left Parent', index=1)
# 	parent_right = fields.Integer('Right Parent', index=1)
# 	@api.constrains('parent_id')
# 	def _check_parent_id(self):
# 		if not self._check_recursion():
# 			raise exceptions.ValidationError('Error ! You can not create recursive tags.')

	# @api.model
	# def name_create(self, name):
	# 	return self.create({'name': name}).name_get()[0]