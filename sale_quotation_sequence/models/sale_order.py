# -*- coding: utf-8 -*-
from odoo import api, models

class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.model
	def create(self, vals):
		vals["name"] = self.env["ir.sequence"].next_by_code("sale.quotation") or _('New')
		return super(SaleOrder, self).create(vals)

	def action_confirm(self):
		for order in self:
			if order.state in ("draft", "sent"):
				if order.origin and order.origin != "":
					quo = order.origin + ", " + order.name
				else:
					quo = order.name
				order.write(
					{
						"origin": quo,
						"name": self.env["ir.sequence"].next_by_code("sale.order"),
					}
				)
		return super(SaleOrder, self).action_confirm()
