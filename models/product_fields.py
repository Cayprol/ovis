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

	name = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], ondelete='restrict', required=True, help='Customer relates to this product')

	pid = fields.Char(string='Product ID', required=True)

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, index=1)

	sequence = fields.Integer(string='Sequence', default=1, help='Assigns the priority to the list of product customer.')