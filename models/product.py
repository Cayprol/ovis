# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp

from odoo.tools import float_compare, pycompat

class InheritProductTemplate(models.Model):

	_inherit = 'product.template'

	drawing = fields.Char(string='Drawaing', help="Engineer Drawing file name.")

	buyer_ids = fields.One2many('product.buyerinfo', 'product_tmpl_id', 'Customers', help="Define customer pricelists.")	
	variant_buyer_ids = fields.One2many('product.buyerinfo', 'product_tmpl_id')

class BuyerInfo(models.Model):
	_name = "product.buyerinfo"
	_description = "Pricelist for customer."
	_order = 'sequence, min_qty desc, price'
	
	name = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)], ondelete='cascade', required=True, help="Customer of this product")
	product_name = fields.Char('Customer Product Name',	help="This customer's product name will be used when printing a request for quotation. Keep empty to use the internal one.")
	product_code = fields.Char('Customer Product Code',	help="This customer's product code will be used when printing a request for quotation. Keep empty to use the internal one.")
	sequence = fields.Integer('Sequence', default=1, help="Assigns the priority to the list of product customer.")
	product_uom = fields.Many2one('uom.uom', 'Unit of Measure', related='product_tmpl_id.uom_po_id', help="This comes from the product form.")
	min_qty = fields.Float('Minimal Quantity', default=0.0, required=True, help="The minimal quantity to sell to this customer, expressed in the customer Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
	price = fields.Float('Price', default=0.0, digits=dp.get_precision('Product Price'), required=True, help="The price to purchase a product")
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, index=1)
	currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id.id, required=True)
	date_start = fields.Date('Start Date', help="Start date for this customer price")
	date_end = fields.Date('End Date', help="End date for this customer price")
	product_id = fields.Many2one('product.product', 'Product Variant', help="If not set, the customer price will apply to all variants of this products.")
	product_tmpl_id = fields.Many2one('product.template', 'Product Template', index=True, ondelete='cascade', oldname='product_id')
	product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count', readonly=False)
	delay = fields.Integer('Delivery Lead Time', default=1, required=True, help="Lead time in days between the confirmation of the sales order and the products going out of your warehouse.")

	description = fields.Text(string='Description', help="Description regarding this Customer's pricing details.")

	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Vendor Pricelists'),
			'template': '/product/static/xls/product_supplierinfo.xls'
		}]