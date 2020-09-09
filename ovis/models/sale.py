# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

	_inherit = 'sale.order'

	@api.model
	def create(self, vals):
		if vals.get('state') == 'sale':
			vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
		else:
			vals['name'] = self.env['ir.sequence'].next_by_code('sale.quotation') or '/'
		return super(SaleOrder, self).create(vals)

	def action_send(self):
		self.ensure_one()
		self.write({'state': 'sent'})
		return True

	def action_confirm_sale_order(self):
		view = self.env.ref('ovis.quote_order_form')
		wiz = self.env['quote.to.order'].create({})
		return {
			'name': _('Create Sales Order?'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'quote.to.order',
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': wiz.id,
			'context': {'parent_model': self._name,
						'parent_id': self.id,},
		}

	@api.depends('order_line.tally')
	def _compute_tally(self):
		for order in self:
			notified = [line.tally for line in order.order_line]
			order.update({'tally': all(notified)})

	# Change 'state' to 'draft', preserve existing behavior.
	# Adding the ability to reset all tallied order_line to False,
	# Refresh delivery date to today() to avoid scheduling delivery in the past.
	def action_draft(self):
		for line in self.order_line:
			line.update({'tally': False,
						'sale_delivery_date': fields.date.today()})
		return super(SaleOrder, self).action_draft()

	@api.onchange('partner_id')
	def onchange_domain_partner_invoice_id(self):
		if self.partner_id:
			res = {'domain': {'partner_invoice_id': [('parent_id.id', '=', self.partner_id.id)]}}
			return res
		else:
			return False

	def write(self, values):
		if values.get('order_line') and self.state == 'sale':

			_logger.info(values['order_line'])

			for order in self:
				to_log={}
				for value in values['order_line']:
					if value[1] is int:
						line = order.order_line.browse(value[1])
						if type(value[2]) == dict:
							if value[2].get('sale_delivery_date'):
								if line.sale_delivery_date != value[2]['sale_delivery_date']:
									_logger.info("Date Changed.")
									to_log[line] = (line.sale_delivery_date, value[2]['sale_delivery_date'])
				if to_log:
					documents = self.env['stock.picking']._log_activity_get_documents(to_log, 'move_ids', 'UP')
					order._log_change_delivery_date(documents)

		return super(SaleOrder, self).write(values)

	def _log_change_delivery_date(self, documents, cancel=False):
		def _render_note_exception_delivery_so(rendering_context):
			order_exceptions, visited_moves = rendering_context
			visited_moves = list(visited_moves)
			visited_moves = self.env[visited_moves[0]._name].concat(*visited_moves)
			order_line_ids = self.env['sale.order.line'].browse([order_line.id for order in order_exceptions.values() for order_line in order[0]])
			sale_order_ids = order_line_ids.mapped('order_id')
			impacted_pickings = visited_moves.filtered(lambda m: m.state not in ('done', 'cancel')).mapped('picking_id')
			values = {
				'sale_order_ids': sale_order_ids,
				'order_exceptions': order_exceptions.values(),
				'impacted_pickings': impacted_pickings,
				'cancel': cancel
			}
			return self.env.ref('ovis.exception_on_so').render(values=values)
		self.env['stock.picking']._log_activity(_render_note_exception_delivery_so, documents)


	tally = fields.Boolean("Tally", compute="_compute_tally", store=True, readonly=True, help="This field indicates all order lines associated to this order are notified for tally or not.")


class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	tally = fields.Boolean("Tally", help="This field indicates the order line has been notified for tally or not.")

	@api.onchange('sale_delivery_date')
	def _onchange_sale_delivery_date(self):
		if self.state in ['sale']: 
			return {
				'warning': {
					'title': _('Delivery Order has been scheduled.'),
					'message': _("Please, double check the scheduled date of all corresponding delivery orders.")
				}
			}