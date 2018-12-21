from odoo import api, fields, models, _

class QualityOrder(models.Model):
	
	_name = 'quality.order'

	origin = fields.Char('Source Document', index=True, help="Reference of the document")

	picking_id = fields.Many2one('stock.picking', 'Picking Order', readonly=True)

	note = fields.Text('Notes')

	state = fields.Selection([
		('draft', 'Draft'),
		('confirmed', 'Waiting'),
		('done', 'Done'),
		('cancel', 'Cancelled'),
		], string='Status', copy=False, index=True, readonly=True, store=True, track_visibility='onchage',
		 help="Draft: not confirmed yet, and not scheduled. notification may or may not pushed.\n"
			  "Waiting: confirmed, and being scheduled, notification pushed.\n"
			  "Done: validated, required actions are made.\n"
			  "Cancelled: been put on hold, not scheduled, no notification.")

	date = fields.Datetime(
		'Creation Date',
		default=fields.Datetime.now, index=True, track_visibility='onchange', readonly=True,
		help="Creation Date, usually the time of the order")

	date_done = fields.Datetime('Date of Validation', copy=False, readonly=True, help="Date of order finishing validation.")

	user_id = fields.Many2one('res.users', string='Examiner', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)

	order_line = fields.One2many('quality.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)




