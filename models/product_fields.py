# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class SaleOrderInherited(models.Model):
# 	_inherit = 'sale.order' 

		
# class ResPartnerInherited(models.Model):
# 	_inherit = 'res.partner'


class ProductTemplateInherited(models.Model):
	
	_inherit = 'product.template'
	
	@api.multi
	def action_view_quotations(self):
		self.ensure_one()
		action = self.env.ref('OVIS.action_product_quotation_list')
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
	@api.depends('product_variant_ids.sales_count')
	def _quotation_count(self):
		for product in self:		
			product.quotation_count = sum([p.quotation_count for p in product.product_variant_ids])
		# return True


	customer_pid = fields.One2many('product.customerinfo', 'product_tmpl_id', string='Customer Product ID')
	
	quotation_count = fields.Integer(compute='_quotation_count' , string='# Quotation')

class ProductProductInherited(models.Model):

	_inherit = 'product.product'

	# @api.multi
	# def _quotation_count(self):
	# 	domain = [
	# 		('state', 'in', ['draft', 'sent']), 
	# 		('product_id', 'in', self.mapped('id')),
	# 		]

	# 	PurchaseOrderLines = self.env['purchase.order.line'].search(domain)
	# 	for product in self:
	# 		product.quotation_count = len(PurchaseOrderLines.filtered(lambda r: r.product_id == product).mapped('order_id'))


	@api.multi
	def _quotation_count(self):
		r = {}
		domain = [
			('state', 'in', ['draft', 'sent']),
			('product_id', 'in', self.ids),
		]
		for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
			r[group['product_id'][0]] = group['product_uom_qty']
		for product in self:
			product.quotation_count = r.get(product.id, 0)
		return r

	quotation_count = fields.Integer(compute='_quotation_count', string='# Quotation')

    # sales_count = fields.Integer(compute='_sales_count', string='# Sales')


class ProductCustomerInfo(models.Model):

	_name = 'product.customerinfo'

	_description = 'Information about a product customer'

	product_tmpl_id = fields.Many2one(
		'product.template', string='Product Template',
		index=True, ondelete='cascade')

	company_id = fields.Many2one(
		'res.company', string='Company', 
		default=lambda self: self.env.user.company_id.id, index=1)

	name = fields.Many2one(
		'res.partner', string='Customer', 
		domain=[('customer', '=', True)], 
		ondelete='cascade', 
		required=True, 
		help="Customer relates to this product")

	product_name = fields.Char(
		string='Vendor Product Name',
		help="This customer's product name.")

	product_code = fields.Char(
		string='Vendor Product Code',
		help="This customer's product code.")







