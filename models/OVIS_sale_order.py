# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherited(models.Model): 

	_inherit = 'sale.order'

	material_prepare = fields.Boolean(string='Material Prepare')

	# Adding a state to exisiting states
	state = fields.Selection(selection_add=[('material_prepare','Material Preparing')])

	# creating order in certain state
	@api.one # @api.multi & ensure_one()
	def action_material_prepare(self):
		self.state = 'material_prepare'

	@api.model
	def _action_confirm(self, values):
        # Override the original create function for the res.partner model
		record = super(sale_order, self)._action_confirm(values)

		if record['material_prepare'] == True:
			# record['state'] = 'material_prepare'
			self.write({'state': 'material_prepare', 'confirmation_date': fields.Datetime.now()})

        # Return the record so that the changes are applied and everything is stored.
	return record

	# @api.multi
	# def _action_confirm(self):
	# 	for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
	# 		order.message_subscribe([order.partner_id.id])
	# 	self.write({
 #            'state': 'sale',
 #            'confirmation_date': fields.Datetime.now()
 #        })
	# 	if self.env.context.get('send_email'):
	# 		self.force_quotation_send()

	# 	create an analytic account if at least an expense product
	# 	if any([expense_policy != 'no' for expense_policy in self.order_line.mapped('product_id.expense_policy')]):
	# 		if not self.analytic_account_id:
	# 			self._create_analytic_account()

	# 	return True

	# @api.multi
	# def action_confirm(self):
	# 	self._action_confirm()
	# 	if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
	# 		self.action_done()
	# 	return True





