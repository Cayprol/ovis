# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	# no trigger product_id.invoice_policy to avoid retroactively changing SO
	@api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
	def _get_to_invoice_qty(self):
		"""
		Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
		calculated from the ordered quantity. Otherwise, the quantity delivered is used.
		"""
		for line in self:
			if line.order_id.state in ['sale', 'done']:
				if line.company_id.force_invoice_policy:
					if line.company_id.default_invoice_policy == 'order':
						line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
					elif line.company_id.default_invoice_policy == 'delivery':
						line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
					else:
						raise ValidationError(_("Force Policy is enabled, but no feasible invoice policy found to calculate Quantity to Invoice."))

				elif line.product_id.invoice_policy == 'order':
					line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
				elif line.product_id.invoice_policy == 'delivery':
					line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
				elif line.display_type:
					line.qty_to_invoice = 0
				else:
					raise ValidationError(_("No feasible invoice policy found to calculate Quantity to Invoice."))
			else:
				line.qty_to_invoice = 0