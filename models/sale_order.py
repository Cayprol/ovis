# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritProductTemplate(models.Model):

	_inherit = 'sale.order'