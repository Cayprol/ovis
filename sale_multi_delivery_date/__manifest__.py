# -*- coding: utf-8 -*-
{
	'name': 'Multi Sales Dates',
	'summary': 'Multiple delivery dates on sales order',
	'description': """
Allow each sales order line to be assigned with a delivery date.
On confirming the sales order, multiple delivery orders are generated according to dates.
If multiple sales order line are assigned with the same date, 
their corresponding stock moves (to client) are generated within the same delivery order. """,
	'version': '1.15',
	'category': 'Sales/Sales',
	'author': 'Cayprol',
	'license': "LGPL-3",
	'application': False,
	'installable': True,
	'auto_install' : False,
	'depends': ['sale', 'sale_stock', 'stock'],
	'data': [
		'views/sale_views.xml',
		],
	'demo': [],
	'test': [],
}