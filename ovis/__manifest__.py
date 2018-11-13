# -*- encoding: utf-8 -*-
{
    'name': "OVIS",
    'version': '12.0.0',
    'summary': 'Custom Module For OVIS.',
    'category': 'Other',
    'description': """Custom Module For OVIS.""",
    'author': 'Cayprol',
    "depends" : ['base', 'mrp', 'product', 'purchase', 'sale', 'web', 'l10n_tw', 'l10n_cn_province'],
    'data': ['security/ir.model.access.csv',
             'views/inherit_product_template_only_form_views.xml',
             'views/product_views.xml',
             'views/inherit_purchase_views.xml',
             'views/inherit_res_partner_views.xml',
             'views/inherit_stock_picking_views.xml',
             ],
    "images": [],
    'license': 'LGPL-3',
    'qweb': [
            ],  
    
    'installable': True,
    'application'   : True,
    'auto_install'  : False,
}
