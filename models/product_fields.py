from odoo import models, fields




class Product_Description(models.Model):

	_name = 'product.description'

	_inherit = 'product.template'

	# id = 'product_description'

	product_description = fields.Text(string='Description for Product')
