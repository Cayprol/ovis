# -*- encoding: utf-8 -*-
{
    'name': "Quality",
    'version': '12.0.0',
    'summary': 'App for Quality Assurance and Quality Control',
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
    'data': [],
    "images": [],
    'license': 'LGPL-3',
    'qweb': [
            ],  
    
    'installable': True,
    'application'   : True,
    'auto_install'  : False,
}
