# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):

	_inherit = 'res.partner'

	def _get_name(self):
		name = super(Partner, self)._get_name()
		partner = self
		if self._context.get('show_ref_city'):
			ref = partner.ref or partner.name
			city = partner.city or 'No City'
			name = ref + ', ' + city + "\n" + partner._display_address()

		return name

	# store=True is critical, by default computed field store=False, the computed method runs on every load of record.
	# On load, partner.parent_id.ref is False on records that do not have parent_id, and this False would be set to 'ref'.
	# Records do have parent_id would get the above False, and set this False to its 'ref'.
	# This results 'ref' on any record is always False
	# store=True breaks this chain, computed method only runs when depending field is modified.
	# Just loading the record does not update any record.
	# When parent_id.ref is modified, its value will be set to 'ref'.
	# The inverse parameter makes computed field editable for the above modification possible.
	ref = fields.Char(string='Reference', index=True, store=True, compute='_compute_ref', inverse='_inverse_ref')

	@api.depends('parent_id.ref')
	def _compute_ref(self):
		for partner in self:
			partner.ref = partner.parent_id.ref

	def _inverse_ref(self):
		for partner in self:
			partner.parent_id.ref = partner.ref

