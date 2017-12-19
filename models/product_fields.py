from odoo import models, fields




class Product_Description(models.Model):

	_name = 'product_description'

	_inherit = 'product.product'

	product_description = fields.Char(string='Description for Product')
