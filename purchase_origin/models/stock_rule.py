# -*- coding: utf-8 -*-
from odoo import api, models
# import logging
# _logger = logging.getLogger(__name__)
class StockRule(models.Model):
	_inherit = 'stock.rule'

	def _replace_origin(self, model_name, domain, parent_id, product_id):
		"""
		Prepare origin names to a string

		:param str model_name: The origin model to search into, the formatted names of this model will be returned
		:param list domain: Condition to search
		:param str parent_id: Due to different models, the Many2one field name in model is different, must have this to get names
		:param recordset product_id: Recordset is relevant based on product_id
		:return: The source document names as 1 string
		:rtype: str
		"""
		origin_ids = self.env[model_name].search(domain)
		origin_ids_with_matching_product = origin_ids.filtered(lambda origin_id: origin_id.product_id == product_id)
		origin_ids_with_matching_product.write({'po_generated': True})

		# 'parent_id' are not the same name in different model, writing it this way to accommodate the change
		origin_names = origin_ids_with_matching_product.mapped('{}.name'.format(parent_id))
		origin = ""
		for name in origin_names:
			origin += "{}, ".format(name)

		return origin[:-2]

	@api.model
	def _run_buy(self, procurements):
		"""
		Override _run_buy during the generation of Buy procurements by replacing 'origin' accordingly in each procurement

		:param list procurements: List contains tuples, each tuple has 2 elements, 1st: nametuple, 2nd: 
		:return: super
		:rtype: func
		"""
		# Retrieve Purchase Order Control setting of current company
		po_origin = self.env.company.po_origin

		# If 'standard', Reordering rule is the source for MTS route
		# Odoo by default is setup this way.
		if po_origin == 'standard':
			return super(StockRule, self)._run_buy(procurements)

		# The new list to replace procurements, which meant to have origin replaced for each procurement
		origin_replaced_procurements = []
		for procurement, rule in procurements:
			# product_id to find all related records in respected models
			product_id = procurement.product_id

			if po_origin == 'delivery':
				domain = [('po_generated', '=', False), ('state', 'in', ['confirmed', 'partially_available'])]
				origin = self._replace_origin('stock.move', domain, 'picking_id', product_id)

			elif po_origin == 'sales':
				domain = [('po_generated', '=', False), '&', ('state', 'in', ['sale', 'done']), ('qty_to_deliver', '>', 0)]
				origin = self._replace_origin('sale.order.line', domain, 'order_id', product_id)

			# namedtuple must use _replace to update attributes, a new instance is produced
			procurement = procurement._replace(origin=origin)
			origin_replaced_procurements.append((procurement, rule))

		return super(StockRule, self)._run_buy(origin_replaced_procurements)
