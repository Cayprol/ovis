# -*- coding: utf-8 -*-
{
    'name': 'Supplierinfo Views',
    'summary': 'Views for supplierinfo',
    'description': """
The standard Odoo module 'product' defines class SupplierInfo, from which module 'purchase' also inherit.
This module does not add any features to standard Odoo.
This module offers views for class SupplierInfo for end users.
""",
    'version': '1.15',
    'category': 'Operations/Purchase',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['product', 'purchase'], 
    'data': [
        'views/product_views.xml',
        ],
    'demo': [],
    'test': [],
}
