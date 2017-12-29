# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class SaleOrderInherited(models.Model):
# 	_inherit = 'sale.order' 

class ProductTemplateInherited(models.Model):
	_inherit = 'product.template'

	customer_pid = fields.One2many('product.customerinfo', 'product_tmpl_id', string='Customer PID')
	

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
			'domain': [('state', 'in', ['sale', 'done']), ('product_id.product_tmpl_id', '=', self.id)],
			
		}
# class ResPartnerInherited(models.Model):
# 	_inherit = 'res.partner'

class ProductCustomerInfo(models.Model):

	_name = 'product.customerinfo'

	_description = 'Information about a product customer'

	name = fields.Many2one('res.partner', string='Customer', index=True, domain=[('customer', '=?', True)], ondelete='restrict', onupdate='cascade', required=True, help='Customer relates to this product')

	product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='restrict', onupdate='cascade', index = True)

	product_code = fields.Char(string='Product Code', required=True, help="This customer's product code will be used when the customer sends request of quotation to us.")

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, index=1)
