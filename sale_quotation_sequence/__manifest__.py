# -*- coding: utf-8 -*-
{
    'name': 'Sales Quotation Sequence',
    'summary': 'Differ Sale Order/Quotation Sequence',
    'description': """
This module differs the sequence of Sales Order and Quotation.
This module is not company specific. All companies share the same quotation and sale order sequence.
""",
    'version': '1.15',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['sale'], 
    'data': [
        'data/ir_sequence_data.xml',
        ],
    'demo': [],
    'test': [],
}
