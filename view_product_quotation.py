from odoo import models, fields

class view_product_quotation(models.Model):
	_name = 'view_product_quotation'

	name = fields.Char(string='name')


class ProductTemplateInherited(models.Model):
	_inherit = 'product.template'

	product_description = fields.Char(string='Description for Product')
