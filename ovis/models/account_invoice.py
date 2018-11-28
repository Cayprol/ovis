# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError


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
					if line.day_of_the_month > 0:
						months_delta = (line.day_of_the_month < next_date.day) and 1 or 0
						next_date += relativedelta(day=line.day_of_the_month, months=months_delta)
				elif line.option == 'after_invoice_month':
					next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
					next_date = next_first_date + relativedelta(days=line.days - 1)

				elif line.option == 'day_following_month':
					next_date += relativedelta(day=line.days, months=1)
				elif line.option == 'day_current_month':
					next_date += relativedelta(day=line.days, months=0)

				elif line.option == 'on_date_after_month':
					next_date += relativedelta(day=line.day_of_the_month, months=line.months)

				result.append((fields.Date.to_string(next_date), amt))
				amount -= amt
		amount = sum(amt for _, amt in result)
		dist = currency.round(value - amount)
		if dist:
			last_date = result and result[-1][0] or fields.Date.today()
			result.append((last_date, dist))
		return result


class InheritAccountPaymentTermLine(models.Model):

	_inherit = 'account.payment.term.line'

	option = fields.Selection(selection_add=[('on_date_after_month', "on date after months")])

	months = fields.Integer(string='Number of Months', help='Number of Months', default=0)

	@api.onchange('option')
	def _onchange_option(self):
		if self.option in ('day_current_month'):
			self.days = 0
			self.months = 0

		elif self.option in ('day_following_month'):
			self.days = 0
			self.months = 0

		elif self.option in ('day_after_invoice_date', 'after_invoice_month'):
			self.day_of_the_month = 0
			self.months = 0

	@api.onchange('months')
	def _onchange_months(self):
		if self.option in ('on_date_after_month'):
			if self.months <= 1:
				raise UserError(_("'Number of Months' must be greater than 1, otherwise 'of the current month' or 'of the following month' should be selected."))
			else:
				self.days = (self.months - 1) * 30

	@api.one
	@api.constrains('day_of_the_month', 'day')
	def _check_days(self):
		if self.option in ('day_following_month', 'day_current_month') and (self.days <= 0 or self.day_of_the_month <= 0):
			raise ValidationError(_("The day of the month used for this term must be stricly positive."))
		elif self.days < 0 or self.day_of_the_month < 0:
			raise ValidationError(_("The number of days used for a payment term cannot be negative."))
