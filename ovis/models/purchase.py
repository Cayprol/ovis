# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	@api.multi
	def button_confirm(self):
		super(PurchaseOrder, self).button_confirm()
		self.write({'user_id': self.env.uid})

		return True