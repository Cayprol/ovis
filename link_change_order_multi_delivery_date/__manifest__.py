{
	'name': 'Link Change Order Multi Delivery Date',
	'version': '13.0.0',
	'category': 'Other',
	'description': 'Link module',
	'depends': 
		[	
			'change_order',
			'sale_multi_delivery_date',
		],
	'data': 
		[	
			'data/mail_data.xml',
			'views/change_order.xml',
			'views/sale_views.xml',
		],
	'license': 'AGPL-3', 
	'installable': True,
	'application'   : False,
	'auto_install'  : True,
}