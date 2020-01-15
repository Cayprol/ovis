from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import datetime

class AccountMove(models.Model):

	_inherit = "account.move"

	def _get_invoice_statement_name(self):
		if any(not move.is_invoice() for move in self):
			raise UserError(_("Only invoices could be printed."))
		if any(True if move.invoice_payment_state in ('paid') else False for move in self ):
			raise UserError(_("Only Not Paid or In Payment Invoices could be printed."))
		return str(datetime.now().strftime('%Y-%m-%d-%H-%M'))

