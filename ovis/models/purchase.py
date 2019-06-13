# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare

class PurchaseOrderLine(models.Model):

	_inherit = 'purchase.order.line'

	qty_qualified = fields.Float(string="Qualified Qty", digits=dp.get_precision('Product Unit of Measure'), copy=False)