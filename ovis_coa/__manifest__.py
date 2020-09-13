# -*- coding: utf-8 -*-
{
    'name': 'OVIS Chart of Account',
    'summary': "Insert records of all chart of accounts",
    'version': '12.0.0',
    'category': 'Localization',
    'author': 'Cayprol',
    "application": False,
    "installable": True,
    'depends': ['account', 'l10n_tw'],
    'data': [
        'data/account_group.xml',
        'data/l10n_ovis_standard_chart.xml',
        'data/account.account.template.csv',
        'data/account_chart_template.xml',
        'data/bank.xml',
    ],
    # 'post_init_hook': 'add_account_journal',
    'demo': [],
    'test': [],
}
