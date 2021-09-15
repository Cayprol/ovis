# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	"""
	Using Many2many field over One2many because
	1. Two conditions to apply for the domain, 
	   One2many would only store 'mrp.bom.line' records which its 'product_tmpl_id' matching current template.id
	   One of the condition contradicts this rule.
	   The contradicted condition is when this template being one of the alternatives.
	2. We do not wish to edit alternative_bom_line_ids from 'product.template', but only from 'mrp.bom' 
	"""
	# alternative_bom_line_ids = fields.One2many('mrp.bom.line', 'product_tmpl_id', string='Alternative BoM Components', domain=[('alternative_product_ids','!=',False)])
	alternative_bom_line_ids = fields.Many2many(
		'mrp.bom.line',
		'product_template_bom_line_rel',
		'product_template_id',
		'bom_line_id', compute="_compute_alternative_bom_line_ids", compute_sudo=True)

	alternative_bom_line_count = fields.Integer('# of BoM Where is Used as Alternative',
									   compute='_compute_alternative_bom_line_count', compute_sudo=True)

	@api.depends('bom_count', 'used_in_bom_count')
	def _compute_alternative_bom_line_ids(self):
		for template in self:
			ids = self.env['mrp.bom.line'].search(
				['|', '&', ('product_tmpl_id', '=', template.id), ('alternative_product_ids', '!=', False),
				 ('alternative_product_ids', 'in', template.product_variant_ids.ids)]).ids
			template.update({'alternative_bom_line_ids': [(6, False, ids)]})

	@api.depends('alternative_bom_line_ids')
	def _compute_alternative_bom_line_count(self):
		for template in self:
			template.alternative_bom_line_count = self.env['mrp.bom'].search_count(
				[('bom_line_ids.alternative_product_ids', 'in', template.product_variant_ids.ids)])