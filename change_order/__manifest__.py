# -*- coding: utf-8 -*-
{
    'name': 'Change Order',
    'summary': 'Modify existing order',
    'description': """
Modify existing sales/purchase workflow to record (approval configurable) changes made to any field affects pricing.
""",
    'version': '13.0.0',
    'category': 'Workflow',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    # inherit sale_stock/purchase_stock for overriding '_compute_qty_delivered_method'/'_compute_qty_received_method'
    'depends': ['purchase_stock', 'sale_stock', 'purchase', 'sale'], 
    'data': [
            'data/ir_sequence_data.xml',
            'data/mail_data.xml',
            'security/ir.model.access.csv',
            'views/change_purchase_order.xml',
            'views/change_sale_order.xml',
            ],
    'demo': [],
    'test': [],
}
