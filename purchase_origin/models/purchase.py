# -*- coding: utf-8 -*-
from odoo import models, fields

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	origin = fields.Char('Source Document', copy=False, readonly=True, help="Reference of the document that generated this purchase order request (e.g. a sales order)")

