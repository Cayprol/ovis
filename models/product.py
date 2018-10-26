# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class InheritProductTemplate(models.Model):

	_inherit = 'product.template'

	drawing = fields.Char(string='Drawaing', help="Engineer Drawing file name.")

	
