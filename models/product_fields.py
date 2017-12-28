from odoo import models, fields, api


# class SaleOrderInherited(models.Model):
# 	_inherit = 'sale.order' 

class ProductTemplateInherited(models.Model):
	_inherit = 'product.template'

	customer_pid = fields.One2many('product.customerinfo', u'name', string='Customer PID')

# class ResPartnerInherited(models.Model):
# 	_inherit = 'res.partner'

class ProductCustomerInfo(models.Model):

	_name = 'product.customerinfo'

	_description = 'Information about a product customer'

	name = fields.Many2one('res.partner', u'Customer', index=True, domain=[(u'customer', '=?', True)], ondelete='restrict', required=True, help='Customer relates to this product')

	pid = fields.Char(string='Product ID', required=True)

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, index=1)
