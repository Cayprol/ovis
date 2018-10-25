# -*- coding: utf-8 -*-
from odoo import models, fields, api

class InheritProductTemplate(models.Model):

	_inherit = 'product.template'

	drawing = fields.Char(string='Drawaing', help="Engineer Drawing file name.")
