from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class QualityOrder(models.Model):
	
	_name = 'quality.order'
	_description = 'Quality Order'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

	READONLY_STATES = {
		'waiting': [('readonly', True)],
		'done': [('readonly', True)],
		'locked': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
	origin = fields.Char('Source Document', index=True, help="Reference of the document")
	picking_id = fields.Many2one('stock.picking', 'Picking Order', readonly=True)
	note = fields.Text('Notes')
	state = fields.Selection([
		('draft', 'Draft'),
		('waiting', 'Waiting'),
		('done', 'Done'),
		('locked', 'Locked'),
		('cancel', 'Cancelled'),
		], string='Status', copy=False, index=True, readonly=True, store=True, default='draft', track_visibility='onchage',
		 help="Draft: not confirmed yet, and not scheduled. notification may or may not pushed.\n"
			  "Waiting: confirmed, being scheduled, notification pushed.\n"
			  "Done: validated, required actions are made.\n"
			  "Cancelled: been put on hold, not scheduled, no notification.")
	date = fields.Datetime(
		'Creation Date',
		default=fields.Datetime.now, index=True, track_visibility='onchange', readonly=True,
		help="Creation Date, usually the time of the order")
	date_done = fields.Datetime('Date of Validation', copy=False, readonly=True, help="Date of order finishing validation.")
	user_id = fields.Many2one('res.users', string='Examiner', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)

	order_line = fields.One2many('quality.order.line', 'order_id', string='Order Lines', states=READONLY_STATES, copy=True)

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('quality.order') or '/'
		return super(QualityOrder, self).create(vals)

	@api.multi
	def unlink(self):
		for order in self:
			if not order.state == 'cancel':
				raise UserError(_('In order to delete a quality order, you must cancel it first.'))
		return super(QualityOrder, self).unlink()

	@api.multi
	def button_confirm(self):
		for order in self:
			if order.state == 'draft':
				order.write({'state': 'waiting'})
		return True

	@api.multi
	def button_validate(self):
		self.ensure_one()
		if self.state == 'waiting':
			view = self.env.ref('quality.wizard_validate_result_form')
			wiz = self.env['validate.result.wizard'].create({})
			return {'name': _('Do these items meet the quality standard?'),
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'validate.result.wizard',
					'views': [(view.id, 'form')],
					'view_id': view.id,
					'target': 'new',
					'res_id': wiz.id,
					'context': self.env.context}
		else:
			raise UserError(_("Must be in state 'Waiting' to be validated."))

	@api.multi
	def button_cancel(self):
		self.ensure_one()
		if self.picking_id:
			view = self.env.ref('quality.wizard_cancel_note_form')
			wiz = self.env['cancelnote.wizard'].create({})
			return {'name': _('Would you like to cancel this order?'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'cancelnote.wizard',
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target': 'new',
				'res_id': wiz.id,
				'context': self.env.context}
		else:
			self.write({'state': 'cancel'})


	@api.multi
	def button_draft(self):
		self.ensure_one()
		if self.state != 'draft':
			self.write({'state': 'draft',
						'date_done': None})
			return True
		else:
			raise UserError(_("State: 'draft' is the only state allowed to be set to draft.  This order is not in such state."))

	@api.multi
	def button_unlock(self):
		self.write({'state': 'done'})


class QualityOrderLine(models.Model):

	_name = 'quality.order.line'	
	_description = 'Quality Order Line'
	_order = 'order_id, sequence, id'

	name = fields.Text(string='Description')
	sequence = fields.Integer(string='Sequence', default=10)
	product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
	qty_done = fields.Float(string="Qty Done", digits=dp.get_precision('Product Unit of Measure'), copy=False)
	product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
	order_id = fields.Many2one('quality.order', string='Order Reference', index=True, required=True, ondelete='cascade')
	company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True, readonly=True)
	product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', required=True)
	product_id = fields.Many2one('product.product', string='Product', change_default=True, required=True)
	state = fields.Selection(related='order_id.state', store=True, readonly=False)
	status = fields.Selection([
		('pending', 'Pending'),
		('qualified', 'Qualified'),
		('rejected', 'Rejected'),
		], string='Status', copy=False, store=True, default='pending', required=True, track_visibility='onchage',
		 help="Waiting: Items are waiting for inspection. Need action!\n"
			  "Qualified: Items meet the standard.\n"
			  "Rejected: Items do NOT meet the standard.")

	@api.multi
	@api.depends('product_uom', 'product_qty', 'product_id.uom_id')
	def _compute_product_uom_qty(self):
		for line in self:
			if line.product_id.uom_id != line.product_uom:
				line.product_uom_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
			else:
				line.product_uom_qty = line.product_qty

