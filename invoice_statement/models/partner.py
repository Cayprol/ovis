from odoo import api, fields, models, _

class ResPartner(models.Model):

	_inherit = 'res.partner'

	total_invoiced_residual = fields.Monetary(compute='_residual_total', string="Total Invoiced", groups='account.group_account_invoice')

	def _residual_total(self):
		account_invoice_report = self.env['account.invoice.report']
		if not self.ids:
			return True

		user_currency_id = self.env.company.currency_id.id
		all_partners_and_children = {}
		all_partner_ids = []
		for partner in self:
			# price_total is in the company currency
			all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
			all_partner_ids += all_partners_and_children[partner]

		# searching account.invoice.report via the ORM is comparatively expensive
		# (generates queries "id in []" forcing to build the full table).
		# In simple cases where all invoices are in the same currency than the user's company
		# access directly these elements

		# generate where clause to include multicompany rules
		where_query = account_invoice_report._where_calc([
			('partner_id', 'in', all_partner_ids), ('state', 'not in', ['draft', 'cancel']),
			('type', 'in', ('out_invoice', 'out_refund')), 
			('invoice_payment_state', 'in', ['not_paid', 'in_payment'])
		])
		account_invoice_report._apply_ir_rules(where_query, 'read')
		from_clause, where_clause, where_clause_params = where_query.get_sql()

		# price_total is in the company currency
		query = """
				  SELECT SUM(residual) as total, partner_id
					FROM account_invoice_report account_invoice_report
				   WHERE %s
				   GROUP BY partner_id
				""" % where_clause
		self.env.cr.execute(query, where_clause_params)
		residual_totals = self.env.cr.dictfetchall()
		for partner, child_ids in all_partners_and_children.items():
			partner.total_invoiced_residual = sum(price['total'] for price in residual_totals if price['partner_id'] in child_ids)


	def action_statement_print(self):

		if self.user_has_groups('account.group_account_invoice'):
			return self.env.ref('invoice_statement.account_statement').report_action(self)
		else:
			return {
				'warning': {
					'title': _('Permission Denied'),
					'message': _("Please, make sure you are in group 'group_account_invoice'.")
				}
			}




	# def action_invoice_print(self):
	# 	""" Print the invoice and mark it as sent, so that we can see more
	# 		easily the next step of the workflow
	# 	"""
	# 	if any(not move.is_invoice(include_receipts=True) for move in self):
	# 		raise UserError(_("Only invoices could be printed."))

	# 	self.filtered(lambda inv: not inv.invoice_sent).write({'invoice_sent': True})
	# 	if self.user_has_groups('account.group_account_invoice'):
	# 		return self.env.ref('account.account_invoices').report_action(self)
	# 	else:
	# 		return self.env.ref('account.account_invoices_without_payment').report_action(self)