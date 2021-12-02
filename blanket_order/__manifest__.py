# -*- coding: utf-8 -*-
{
    'name': 'Blanket Order',
    'summary': 'Blanket Order',
    'description': """
This module offers blanket order for sales and purchase.
On creation, a blanket order doesn't affect inventory needs (no Sales Order/Delivery Order/RFQ/Manufacturing Order).
A blanket order is used to created multiple sales orders or purchase orders.
The blanket order lines qty are deducted based on the orders created from it.
""",
    'version': '1.15',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['account', 'sale', 'purchase'], 
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/blanket_order_sale.xml',
        # 'views/blanket_order_line.xml',
    ],
    'demo': [],
    'test': [],
}