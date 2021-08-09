{
	'name': 'Link Sale Margin Account',
	'version': '13.0.0',
	'category': 'Other',
	'description': 'Link module',
	'depends': 
		[
			'sale_margin',
		],
	'data': 
		[
			'views/account_move_views.xml',
		],
	'license': 'AGPL-3', 
	'installable': True,
	'application'   : False,
	'auto_install'  : True,
}