# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SupplierInfo(models.Model):
	_inherit = "product.supplierinfo"

	# This field created for multi-currency comparison purpose.
	intrinsic_price = fields.Float('Intrinsic Price', digits='Product Price', compute='_compute_intrinsic_price', help="The intrinsic price for multi-currency comparison using company currency.")

	@api.depends('currency_id', 'price')
	def _compute_intrinsic_price(self):
		for info in self:
			info.intrinsic_price = info.price / info.currency_id.rate


class ProductProduct(models.Model):
	_inherit = 'product.product'

	"""
	_prepare_sellers() and _select_seller() are run by "Run Scheduler" which is a threaded implementation.
	If Cursor not closed explicit error occurs, restart postgresql and odoo do NOT resolve.
	Undo all modification to these 2 methods by uninstall this addon, and "Run Scheduler" at its default form at least 1 time.
	"""

	def _prepare_sellers(self, params):
		"""
		Odoo sort supplierinfo by (s.sequence, -s.min_qty, s.price, s.id)
		This method changes the sort condition to (s.intrinsic_price, s.min_qty, s.delay, s.sequence, s.id)
	
		:rtype: recordset 'product.supplierinfo'
		:return: Sorted supplier offers considering currency exchange rate
		"""
		res = super(ProductProduct, self)._prepare_sellers(params=params)	
		return res.sorted(key=lambda s: (s.intrinsic_price, s.min_qty, s.delay, s.sequence, s.id))

	# def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
	"""
	validate date_start and date_end has been built in default odoo
	validate min_qty has been built in default odoo
	"""
	# 	return super(ProductProduct, self)._select_seller(partner_id=partner_id, quantity=quantity, date=date, uom_id=uom_id, params=params)
