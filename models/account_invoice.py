# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
class InheritAccountInvoice(models.Model):

	_inherit = 'account.invoice'

	amount_tax_signed = fields.Monetary(string='Tax Signed', store=True, readonly=True, compute='_compute_amount', currency_field='company_currency_id')

	# temp = fields.Many2one('account.payment.term', string="temp")
	temp = fields.Boolean(string='Temp')

	# @api.onchange('temp')
	# @api.depends('temp')
	# @api.multi
	# def _filter_company(self):
	# 	match_company = self.env['account.payment.term'].search([('company_id.id', '=', self.env.user.company_id.id)])

	# 	self.write({'payment_term_id': match_company})


	@api.multi 
	@api.onchange('temp')
	def on_change_company_id(self):
		res= {}
		term_list= []	
		if self.company_id:
			payment_term = self.env['account.payment.term']
			payment_term_ids = payment_term.search([('company_id','=', self.company_id.id)]) 
			for record in payment_term_ids:
				term_list.append(record.id)	
		res= {'domain':{'company_id':[('id', 'in', term_list)]}} 
		return res

class InheritAccountPaymentTermLine(models.Model):

	_inherit = 'account.payment.term.line'

	option = fields.Selection(selection_add=[('fix_day_after_following_month', 'First day after the next following month ')])

class InheritAccountPaymentTerm(models.Model):

	_inherit = 'account.payment.term'

	@api.one
	def compute(self, value, date_ref=False):
		date_ref = date_ref or fields.Date.today()
		amount = value
		sign = value < 0 and -1 or 1
		result = []
		if self.env.context.get('currency_id'):
			currency = self.env['res.currency'].browse(self.env.context['currency_id'])
		else:
			currency = self.env.user.company_id.currency_id
		for line in self.line_ids:
			if line.value == 'fixed':
				amt = sign * currency.round(line.value_amount)
			elif line.value == 'percent':
				amt = currency.round(value * (line.value_amount / 100.0))
			elif line.value == 'balance':
				amt = currency.round(amount)
			if amt:
				next_date = fields.Date.from_string(date_ref)
				if line.option == 'day_after_invoice_date':
					next_date += relativedelta(days=line.days)
				elif line.option == 'fix_day_following_month':
					next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
					next_date = next_first_date + relativedelta(days=line.days - 1)

				elif line.option == 'fix_day_after_following_month':
					next_first_date = next_date + relativedelta(day=1, months=2)  # Getting 1st of next next month
					next_date = next_first_date + relativedelta(days=line.days - 30)

				elif line.option == 'last_day_following_month':
					next_date += relativedelta(day=31, months=1)  # Getting last day of next month
				elif line.option == 'last_day_current_month':
					next_date += relativedelta(day=31, months=0)  # Getting last day of next month
				result.append((fields.Date.to_string(next_date), amt))
				amount -= amt
		amount = sum(amt for _, amt in result)
		dist = currency.round(value - amount)
		if dist:
			last_date = result and result[-1][0] or fields.Date.today()
			result.append((last_date, dist))
		return result
