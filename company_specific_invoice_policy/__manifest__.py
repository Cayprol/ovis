# -*- coding: utf-8 -*-
{
    'name': 'Company Specific Invoice Policy',
    'summary': "Make invoicing policy company specific",
    'description': """
This module makes sales and purchase invoicing policy company specific. 
    """,
    'version': '13.0.0',
    'category': 'Other',
    'author': 'Cayprol',
    'license': "LGPL-3",
    'application': False,
    'installable': True,
    'auto_install' : False,
    'depends': ['purchase', 'sale'],
    'data': ['views/res_config_settings_views.xml'],
    'demo': [],
    'test': [],
}