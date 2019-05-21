# -*- encoding: utf-8 -*-
{
    'name': "Quality",
    'version': '12.0.0',
    'summary': 'Quality Assurance and Control',
    'category': 'Other',
    'description': """
                    This Application is designed to work with Inventory App.
                    Create entire separate menus for Quality Department including groups/access rights.
                    Forms with Alerts corresponding to Outgoing and Incoming stock movement.
                   """,
    'author': 'Cayprol',
    "depends" : ['base',
                 'product',
                 'stock',
                 ],
    'data': ['data/quality_data.xml',
             'security/quality_security.xml',
             'security/ir.model.access.csv',
             'views/quality_views.xml',
             'views/res_config_settings_views.xml',
             'wizard/cancel_note.xml',
             'wizard/validate_result.xml',
             ],
    "images": [],
    'license': 'LGPL-3',
    'qweb': [
            ],  
    
    'installable': True,
    'application'   : True,
    'auto_install'  : False,
}
