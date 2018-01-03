# -*- coding: utf-8 -*-
{
    'name': "OVIS",

    'summary': """Custom Module for OVIS""",

    'description': """
        OVIS  module for daily operation:
            - Additional Product Fields
            - Additional Shortcut to Views
    """,

    'author': "Cayprol",
    'website': "http://www.ovis.com.tw",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/OVIS_product_template.xml',
        'views/OVIS_product_template_purchase_button_inherit.xml',
        
    ],
}

