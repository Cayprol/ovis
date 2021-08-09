# -*- coding: utf-8 -*-
{
    'name': 'Common Vendors',
    'summary': 'Default common suppliers',
    'description': """
By Odoo default, supplier info are company-specific while multi-company enabled.\n
This module does not remove feature from Odoo, only change default behavior.\n
When installed, newly created supplier info has the default company set to None.\n
User can still manually specify a company.\n
If a company is manually specified, particular supplier info behaves as Odoo default. 
""",
    'version': '13.0.0',
    'category': 'Operations/Purchase',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['product', 'purchase'], 
    'data': [
        ],
    'demo': [],
    'test': [],
}
