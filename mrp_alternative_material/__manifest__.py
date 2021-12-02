# -*- coding: utf-8 -*-
{
    'name': 'Alternative Material',
    'summary': 'BoM Alternative Material',
    'description': """
List alternative materials in BoM.\n
User must manually cancel the existing MO and recreate a new MO with alt-material.\n
""",
    'version': '1.15',
    'category': 'Manufacturing/Manufacturing',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['mrp', 'product'], 
    'data': [
        'views/mrp_bom_views.xml',
        'views/product_views.xml',
        ],
    'demo': [],
    'test': [],
}
