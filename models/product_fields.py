# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class SaleOrderInherited(models.Model):
# 	_inherit = 'sale.order' 

		
# class ResPartnerInherited(models.Model):
# 	_inherit = 'res.partner'


class ProductTemplateInherited(models.Model):
	_inherit = 'product.template'

	customer_pid = fields.One2many('product.customerinfo', 'product_tmpl_id', string='Customer Product ID')
	
	quotation_count = fields.Integer(compute='_quotation_count' , string='# Quotation')

	@api.multi
	def action_view_quotations(self):
		self.ensure_one()
		action = self.env.ref('sale.action_product_sale_list')
		product_ids = self.with_context(active_test=False).product_variant_ids.ids

		return {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': action.target,
			'context': "{'default_product_id': " + str(product_ids[0]) + "}",
			'res_model': action.res_model,
			'domain': [('state', 'in', ['draft', 'sent']), ('product_id.product_tmpl_id', '=', self.id)],
			# 'domain': [('state', 'in', ['sale', 'done']), ('product_id.product_tmpl_id', '=', self.id)],		
		}

	@api.multi
	@api.depends('product_variant_ids.quotation_count')
	def _quotation_count(self):
		for product in self:
			product.quotation_count = sum([p.quotation_count for p in product.product_variant_ids])

class ProductCustomerInfo(models.Model):
# class SupplierInfo(models.Model):
	_name = 'product.customerinfo'

	_description = 'Information about a product customer'
    
	_order = 'sequence, min_qty desc, price'
	
	name = fields.Many2one(
		'res.partner', 'Vendor',
		domain=[('supplier', '=', True)], ondelete='cascade', required=True, 
		help="Vendor of this product")

    product_name = fields.Char('Vendor Product Name', help="This vendor's product name will be used when printing a request for quotation. Keep empty to use the internal one.")

	product_code = fields.Char(
		'Vendor Product Code', 
		help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")

    sequence = fields.Integer( 
    	'Sequence', default=1, help="Assigns the priority to the list of product vendor.")

	product_uom = fields.Many2one(
		'product.uom', 'Vendor Unit of Measure', 
		readonly="1", related='product_tmpl_id.uom_po_id',
		help="This comes from the product form.")

    min_qty = fields.Float(
		'Minimal Quantity', default=0.0, required=True, 
    	help="The minimal quantity to purchase from this vendor, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    
	price = fields.Float(
		'Price', default=0.0, digits=dp.get_precision('Product Price'),
		required=True, help="The price to purchase a product")
    
	company_id = fields.Many2one(
		'res.company', 'Company',
		default=lambda self: self.env.user.company_id.id, index=1)
    
	currency_id = fields.Many2one(
		'res.currency', 'Currency',
		default=lambda self: self.env.user.company_id.currency_id.id,
		required=True)

	date_start = fields.Date('Start Date', help="Start date for this vendor price")
	date_end = fields.Date('End Date', help="End date for this vendor price")
	product_id = fields.Many2one(
		'product.product', 'Product Variant',
		help="If not set, the vendor price will apply to all variants of this products.")
	product_tmpl_id = fields.Many2one(
		'product.template', 'Product Template',
		index=True, ondelete='cascade', oldname='product_id')
	product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
	delay = fields.Integer(
		'Delivery Lead Time', default=1, required=True,
		help="Lead time in days between the confirmation of the purchase order and the receipt of the products in your warehouse. Used by the scheduler for automatic computation of the purchase order planning.")

# 	_name = 'product.customerinfo'

# 	_description = 'Information about a product customer'

# 	# name = fields.Many2one('res.partner', string='Customer', index=True, domain=[('customer', '=?', True)], ondelete='restrict', onupdate='cascade', required=True, help='Customer relates to this product')
# 	name = fields.Many2one(
# 		'res.partner', string='Customer', 
# 		domain=[('customer', '=', True)], 
# 		ondelete='cascade', 
# 		required=True, 
# 		help="Customer relates to this product")

# 	product_name = fields.Char(
# 		string='Vendor Product Name',
# 		help="This customer's product name.")

# 	product_code = fields.Char(
# 		string='Vendor Product Code',
# 		help="This customer's product code.")

# 	# product_code = fields.Char(string='Customer PID', required=True, index=True, help="This customer's product code will be used when the customer sends request of quotation to us.")

# 	# product_tmpl_id = fields.Many2one('product.template', string='Product Name', ondelete='restrict', onupdate='cascade', index = True, readonly=True)

# 	company_id = fields.Many2one(
# 		'res.company', string='Company', 
# 		default=lambda self: self.env.user.company_id.id, index=1)

# 	product_tmpl_id = fields.Many2one(
# 		'product.template', 'Product Template',
# 		index=True, ondelete='cascade')



