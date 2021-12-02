# -*- coding: utf-8 -*-
{
    'name': 'Link OVIS and Sale Stock',
    'version': '1.15',
    'category': 'Other',
    'description': 'Link module',
    'depends': ['ovis', 'sale_stock'],
    'data': 
        [   
            'views/sale_order_views.xml',
        ],
    'license': 'AGPL-3', 
    'installable': True,
    'application'   : False,
    'auto_install'  : True,
}