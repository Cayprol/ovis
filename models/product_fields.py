from odoo import models, fields, api


class SaleOrderInherited(models.Model):
	_inherit = 'sale.order' 

	custom_field = fields.Char(string='Custom Field')

class ProductInformation(models.Model):
	_inherit = 'product.template'

	afield = fields.Char(string='Atest') 

	customer_pid = fields.One2many('product.customerinfo', 'name', string='Customer PID')


class ProductCustomerInfo(models.Model):

	_name = 'product.customerinfo'

	_description = 'Information about a product customer'

	name = fields.Many2one('res.partner', 'Customer', required=True, domain=[('customer', '=', True)], ondelete='restrict', onupdate='cascade')

	pid = fields.Char(string='Product ID', required=True)
