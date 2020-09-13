# -*- coding: utf-8 -*-
{
    'name': 'Sales Back Order',
    'summary': "View backordered Sales",
    'version': '12.0.0',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['account', 'sale_management'],
    'data': ['report/report_order_line.xml',
            'report/sale_order_line_report.xml',
            'views/sale_views.xml',],
    'demo': [],
    'test': [],
}
