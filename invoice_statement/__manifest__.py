# -*- coding: utf-8 -*-
{
    'name': 'Invoice Statement',
    'summary': "Views and Reports for invoice statement.",
    'version': '13.0.0.0.0',
    'category': 'Invoicing',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['account', 'base', 'sale', 'purchase', 'web'],
    'data': ['report/account_report.xml',
            'report/report_invoice.xml',
            'views/account_move_views.xml',
            'views/res_partner_views.xml',
    ],
    'demo': [],
    'test': [],
}
