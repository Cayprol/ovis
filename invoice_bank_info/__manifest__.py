# -*- coding: utf-8 -*-
{
    'name': 'Invoice with Bank Information',
    'summary': "Print invoice with option to display banking information.",
    'version': '13.0.0.0.0',
    'category': 'Invoicing',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['account', 'base', 'sale_management', 'web'],
    'data': ['report/account_report.xml',
             'report/report_invoice.xml',
    ],
    'demo': [],
    'test': [],
}
