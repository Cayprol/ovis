from odoo import models, fields, api


class SaleOrderInherited(models.Model):
	_inherit = 'sale.order' 

	custom_field = fields.Char(string='Custom Field')

class ProductInformation(models.Model):
	_inherit = 'product.template'

	afield = fields.float('Atest') 
	customer_pid = fields.one2many('res.partner', 'name', string='customer_pid')

