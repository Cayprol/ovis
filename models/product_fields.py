from odoo import models, fields, api


class SaleOrderInherited(models.Model):
	_inherit = 'sale.order' 

	custom_field = fields.Char(string='Custom Field')

class ProductTemplateInherited(models.Model):
	_inherit = 'product.template' 

	customer_item = fields.Char(string='Custom Item')

