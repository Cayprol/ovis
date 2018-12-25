from odoo import api, fields, models, _

class QualityOrder(models.Model):
	
	_name = 'quality.order'
	_description = 'Quality Order'


	READONLY_STATES = {
		'waiting': [('readonly', True)],
		'done': [('readonly', True)],
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
		('cancel', 'Cancelled'),
		], string='Status', copy=False, index=True, readonly=True, store=True, default='draft',track_visibility='onchage',
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
	order_line = fields.One2many('quality.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('quality.order') or '/'
		return super(QualityOrder, self).create(vals)

class QualityOrderLine(models.Model):

	_name = 'quality.order.line'	

	_description = 'Quality Order Line'

	_order = 'order_id, sequence, id'

	sequence = fields.Integer(string='Sequence', default=10)

	order_id = fields.Many2one('quality.order', string='Order Reference', index=True, required=True, ondelete='cascade')
	product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', required=True)
	product_id = fields.Many2one('product.product', string='Product', change_default=True, required=True)
	payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')



