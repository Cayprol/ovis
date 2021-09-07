{
	'name': 'Link Sale Margin Change Order',
	'version': '13.0.0',
	'category': 'Other',
	'description': 'Link module',
	'depends': 
		[	
			'change_order',
			'sale_margin',
		],
	'data': 
		[	
			'views/sale_views.xml',
		],
	'license': 'AGPL-3', 
	'installable': True,
	'application'   : False,
	'auto_install'  : True,
}