# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
    	if vals.get('approved_order_id'):
	    	vals['order_id'] = False
    	return super(SaleOrderLine, self).create(vals)
