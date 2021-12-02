# -*- coding: utf-8 -*-
{
    'name': 'Sales Enhanced Views',
    'summary': 'Enhanced sale views',
    'description': """
This module does not include fields created by 3rd party addons.
This module prefers to override standard Odoo views, and only add new views/window action if conflicting other modules.
""",
    'version': '1.15',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['sale'], 
    'data': [
        'views/sale_views.xml',
        ],
    'demo': [],
    'test': [],
}
