# -*- coding: utf-8 -*-
{
    'name': 'Puchase Origin',
    'summary': "Purchase Order Origin Change",
    'description': """
This module introduces 2 logics of how purchase order aquire its source document.  
Depends on the setting, it can be based on Delivery Order or Sales Order. 
    """,
    'version': '13.0.0',
    'category': 'Other',
    'author': 'Cayprol',
    'license': "LGPL-3",
    'application': False,
    'installable': True,
    'auto_install' : False,
    'depends': ['purchase', 'sale_stock', 'stock'],
    'data': [
                'views/purchase_views.xml',
                'views/res_config_settings_views.xml',
            ],
    'demo': [],
    'test': [],
}