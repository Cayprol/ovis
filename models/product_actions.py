# -*- coding: utf-8 -*-

from odoo import models, fields, api

# @api.multi
# def action_view_sales(self):
# 	self.ensure_one()
# 	action = self.env.ref('sale.action_prodcut_sale_list')
# 	product_ids = self.with_context(active_test=False).product_variant_ids.ids

# 	return {
# 		'name': action.name,
# 		'help': action.help,
# 		'type': action.type,
# 		'view_type': action.view_type,
# 		'view_mode': action.view_mode,
# 		'target': action.target,
# 		'context': "{'default_product_id': " + str(product_ids[0]) + "}",
# 		'res_model': action.res_model,
# 		'domain': [('state', 'in', ['sale', 'done']), ('product_id.product_tmpl_id', '=', self.id)],

# 	}

