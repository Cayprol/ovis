# -*- coding: utf-8 -*-
{
    'name': 'Link OVIS and Multi Sales Dates',
    'version': '1.15',
    'category': 'Other',
    'description': 'Link module',
    'depends': ['ovis', 'sale_multi_delivery_date'],
    'data': 
        [   
            'views/sale_views.xml',
        ],
    'license': 'AGPL-3', 
    'installable': True,
    'application'   : False,
    'auto_install'  : True,
}