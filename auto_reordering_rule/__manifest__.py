# -*- coding: utf-8 -*-
{
    'name': 'Auto Reordering Rule',
    'summary': "Auto-creation of reordering rule",
    'description': """
Create a new Product would trigger creation of Orderpoint if the product is Storable.  
    """,
    'version': '13.0.0',
    'category': 'Other',
    'author': 'Cayprol',
    'license': "LGPL-3",
    'application': False,
    'installable': True,
    'auto_install' : False,
    'depends': ['product','stock'],
    'data': [],
    'demo': [],
    'test': [],
}