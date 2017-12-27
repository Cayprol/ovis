from odoo import models, fields, api


class SaleOrderInherited(models.Model):
	_inherit = 'sale.order' 

	custom_field = fields.Char(string='Custom Field')

class ProductInformation(models.Model):
	_inherit = 'product.template'

	afield = fields.Char(string='Atest') 

	pid = fields.One2many('product.customerinfo', 'customers')


class ProductCustomerInfo(models.Model):

	_name = 'product.customerinfo'

	_description = 'Information about a product customer'

	customers = fields.Many2one('res.partner', 'Customers')

	pid = fields.Char(string='Product ID')
