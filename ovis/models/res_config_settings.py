# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	# module_change_order = fields.Boolean(string='Change Orders')
	module_sale_multi_delivery_date = fields.Boolean(string='Multiple Delivery Dates')
	module_sale_quotation_sequence = fields.Boolean(string='Separate Quotation Sequence')
	# module_chinese_conversion = fields.Boolean(string='Mix-search Chinese')
	# module_purchase_common_vendor = fields.Boolean(string='Common Vendors')
	module_purchase_vendor_select = fields.Boolean(string='Smart Vendor Select')
	module_mrp_common_bom = fields.Boolean(string='Common Bill of Materials')
	module_mrp_alternative_material = fields.Boolean(string='Alternatives')
	# module installation Boolean fields do not need to have config_parameter to be saved. in TransientModel
	# (config_parameter='ovis.config_parameter')