# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class InheritPicking(models.Model):

	_inherit = 'stock.picking'

	forwarder_id = fields.Many2one('res.partner', 'Forwarder', help="Forwarder delevering the order.", domain="[('forwarder','=', True)]")




