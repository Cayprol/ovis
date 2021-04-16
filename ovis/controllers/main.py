from odoo import http

class Products(http.Controller):
	@http.route('/products', auth='user')
	def list(self, **kwargs):
		product = http.request.env['product.template']
		products = product.search([])
		return http.request.render('product.product_template_tree_view', {'products': products})