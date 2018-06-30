# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class InheritProductTemplate(models.Model):
	
	_inherit = 'product.template'
	# _parent_name = "parent_id"
	# _parent_store = True
	# _parent_order = 'name'
	
	memo = fields.Text(string='Memorandum', translate=True)

	buyer_ids = fields.One2many('product.purchaserinfo', 'product_tmpl_id', string='Customers')	
	
	drawing = fields.Char(string='Drawaing', help="Engineer Drawing file name.")
	tooling_ids = fields.Many2many(comodel_name='product.template', relation='product_template_rel', column1='tooling_ids', column2='producing_ids', string="Tooling")
	producing_ids = fields.Many2many(comodel_name='product.template', relation='product_template_rel', column1='producing_ids', column2='tooling_ids', string="Producing")
	tooling = fields.Boolean(string='Is Tooling', index=True, default=False)
	# parent_id = fields.Many2one('product.template', string='Parent', index=True, ondelete='cascade', domain="[('tooling','!=',True)]")
	# child_ids = fields.One2many('product.template', 'parent_id', string='Old Versions')	
	# parent_left = fields.Integer('Left Parent', index=1)
	# parent_right = fields.Integer('Right Parent', index=1)
	arrival = fields.Date(string='Arrival Date', help="Arrival Date when this tooling comes in stock.")

	# @api.constrains('parent_id')
	# def _check_parent_id(self):
	# 	if not self._check_recursion():
	# 		raise ValidationError('Error ! You can not create recursive tags.')
	# 	if self.parent_id.tooling == True:
	# 		raise ValidationError('Error ! Parent cannot have be tooling product.')

	# @api.constrains('tooling', 'parent_id')
	# def _check_tooling_parent_id(self):
	# 	if self.tooling == False and self.parent_id != None:
	# 		raise ValidationError('Error ! Non-tooling product cannot have parent.')

	# @api.constrains('tooling', 'child_ids')
	# def _check_tooling_child_ids(self):
	# 	if self.tooling == True and len(self.child_ids) != 0:
	# 		raise ValidationError('Error ! Tooling product cannot have children.')


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
