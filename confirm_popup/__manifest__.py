# -*- coding: utf-8 -*-
{
    'name': 'Confirm Popup',
    'summary': "Confirmation wizard",
    'description': """
Provide a popup wizard to be chained after any method that runs update() in the end.
It is deisgned for confirmation purpose to avoid accidentally button hit.
Offers note logging for particular record that run update().
Only singleton is allowed.
    """,
    'version': '12.0.0',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['base'],
    'data': ['wizard/confirm_popup.xml'],
    'demo': [],
    'test': [],
}
