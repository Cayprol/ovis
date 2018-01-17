# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherited(models.Model): 

	_inherit = 'sale.order'

	is_prepare = fields.Boolean(string='Material Prepare')

	# # Adding a state to exisiting states
	state = fields.Selection(selection_add=[('material_prepare','Material Preparing')])

	@api.multi
	def action_prepare_material(self):
		if self.is_prepare == True:
			self.write({'state': 'material_prepare', 'confirmation_date': fields.Datetime.now()})

		return True

	@api.model
	def _action_confirm(self):

		record = super()._action_confirm()

		if self.is_prepare == True:
			self.write({'state': 'material_prepare', 'confirmation_date': fields.Datetime.now()})


####################################################################################
	# @api.multi
	# def action_prepare_material(self):
	# 	for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
	# 		order.message_subscribe([order.partner_id.id])

	# 	self.write({'state': 'material_prepare', 'confirmation_date': fields.Datetime.now()})

	# 	if self.env.context.get('send_email'):
	# 		self.force_quotation_send()

	# 	return True
####################################################################################


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





