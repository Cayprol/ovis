# -*- coding: utf-8 -*-
{
    'name': 'Common BoM',
    'summary': 'Default common BoM',
    'description': """
By Odoo default, BoMs are company-specific while multi-company enabled.\n
This module does not remove feature from Odoo, only change default behavior.\n
When installed, newly created BoM has the default company set to None.\n
User can still manually specify a company on existing BoMs.\n
If a company is manually specified, particular BoM behaves as Odoo default. 
""",
    'version': '1.15',
    'category': 'Manufacturing/Manufacturing',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['mrp', 'product'], 
    'data': [
        ],
    'demo': [],
    'test': [],
}
