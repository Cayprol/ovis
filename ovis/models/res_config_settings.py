# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sale_multi_delivery_date = fields.Boolean(string='Multiple Delivery Dates')