# -*- coding: utf-8 -*-
{
    'name': 'Sales Change Order',
    'summary': 'Change Sales Order',
    'description': """
Modify existing workflow to record and approve(configurable) actions on changing confirmed sales order.
""",
    'version': '13.0.0',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['purchase', 'sale', 'sale_management'],
    'data': [
            'data/ir_sequence_data.xml',
            'security/ir.model.access.csv',
            'views/window_actions.xml',
            'views/sale_views.xml',
            'views/change_order.xml',
            ],
    'demo': [],
    'test': [],
}
