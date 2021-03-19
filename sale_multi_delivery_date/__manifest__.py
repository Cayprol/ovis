# -*- coding: utf-8 -*-
{
	'name': 'Multiple Sales Delivery Dates',
	'summary': """Creates multiple delivery orders according to sales order lines.""",
	'version': '13.0.0',
	'category': 'Sales/Sales',
	'author': 'Cayprol',
	'license': "LGPL-3",
	'application': False,
	'installable': True,
	'auto_install' : False,
	'depends': ['sale', 'sale_management', 'sale_stock', 'stock'],
	'data': [
		'views/sale_views.xml',
		'views/stock_picking_views.xml',
		],
	'demo': [],
	'test': [],
}