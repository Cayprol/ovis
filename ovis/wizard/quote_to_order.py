# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class QuoteToOrder(models.TransientModel):

	_name = 'quote.to.order'
	_description = 'Wizard to convert Quote/RFQ to SO/PO'

	note = fields.Text('Note', help="Log note. quotation -> order.")

	# Search the sale.order or purchase.order with model name and id number.
	# Duplicate the order with copy() and pass dict to override the duplicated order.
	# Duplicated values are the 'state', 'origin'.
	# The code implements different ir.sequence are written at sale.py create()
	# On creation if 'state' is 'sale', another ir.sequence is taken.
	def action_confirm(self):
		parent_model = self._context['parent_model']
		parent_id = self._context['parent_id']
		quote = self.env[parent_model].browse(parent_id)
		order = quote.copy({
				'state': 'sale',
				'origin': quote.name,
				})

		if self.note and not self.note.isspace():
			msg = _("Confirm order log note: \r\t{}".format(self.note))
			order.message_post(body=msg)

		# Go to the form view of the duplicated order.
		return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': parent_model,
				'target': 'current',
				'res_id': order.id,
			} 

