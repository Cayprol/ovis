# -*- coding: utf-8 -*-
{
    'name': 'Confirm Popup',
    'summary': "Confirmation wizard",
    'description': """
Provide a popup wizard that run function based on context.  
    """,
    'version': '13.0.0',
    'category': 'Operations/Purchase',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['base'],
    'data': [
            'wizard/confirm_popup.xml',
            'security/ir.model.access.csv',
            ],
    'demo': [],
    'test': [],
}
