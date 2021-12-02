# -*- coding: utf-8 -*-
{
    'name': 'Contacts Enhanced Views',
    'summary': 'Enhanced contact views',
    'description': """
This module does not add any new fields.
This module does not include fields created by 3rd party addons.
This module prefers to override standard Odoo views, and only add new views/window action if conflicting other modules.
""",
    'version': '1.15',
    'category': 'Tools',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['base'], 
    'data': [
        'views/res_partner_views.xml',
        ],
    'demo': [],
    'test': [],
}
