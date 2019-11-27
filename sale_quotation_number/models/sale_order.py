# -*- coding: utf-8 -*-
# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
	_inherit = 'res.company'

	keep_name_so = fields.Boolean(
		string="Use Same Enumeration",
		help="If this is unchecked, quotations use a different sequence from "
			 "sale orders", default=True)


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	keep_name_so = fields.Boolean(related='company_id.keep_name_so', readonly=False)


class SaleOrder(models.Model):
	_inherit = "sale.order"

	def copy(self, default=None):
		self.ensure_one()
		if default is None:
			default = {}
		default['name'] = '/'
		if self.origin and self.origin != '':
			default['origin'] = self.origin + ', ' + self.name
		else:
			default['origin'] = self.name
		return super(SaleOrder, self).copy(default)

	@api.model
	def create(self, vals):
		company = self.env.company
		if not company.keep_name_so:
			vals['name'] = self.env['ir.sequence'].next_by_code(
				'sale.quotation') or '/'
		return super(SaleOrder, self).create(vals)

	def action_confirm(self):
		if super(SaleOrder, self).action_confirm():
			company = self.env.company
			_logger.info(company)
			for order in self:
				_logger.info(order.state)
				if order.state in ('sale', 'done'):
					_logger.info("State is sale/done")
					if not company.keep_name_so:
						_logger.info("ENTERED")
						if order.origin and order.origin != '':
							quo = order.origin + ', ' + order.name
						else:
							quo = order.name
						order.write({
							'origin': quo,
							'name': self.env['ir.sequence'].next_by_code(
								'sale.order')
							})
					else:
						_logger.info("NOT ENTERED")
				else:
					_logger.info("State isn't sale")

		return True
