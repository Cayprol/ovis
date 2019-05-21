# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResCompany(models.Model):
	
	_inherit = 'res.company'

	qo_lead = fields.Integer(string='Days For Process', default=0, help="Number of days allowed for quality orders until it's considered as late.")