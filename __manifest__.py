# -*- coding: utf-8 -*-
{
    'name': "OVIS",

    'summary': """Custom Module for OVIS""",

    'description': """
        OVIS  module for daily operation:
            - Additional Product Fields
            - Additional Shortcut to Views
    """,
    'installable': True,
    'application': True,
    
    'author': "Cayprol",
    'website': "http://www.ovis.com.tw",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'TEST',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'sale', 'purchase', 'product', 'stock', 'mrp', 'ovis_theme'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_product_supplierinfo_form_view.xml',
        'views/inherit_product_template_only_form_views.xml',
        'views/inherit_purchase_order_form.xml',
        'views/inherit_stock_picking_views.xml',
        # 'views/inherit_invoice_supplier_tree_views.xml',
        'views/inherit_view_partner_form.xml',
        'views/inherit_view_order_form.xml',
        'views/stock_picking_shipping.xml',
        'views/invoice_menu.xml',
        'views/sales_menu.xml',
        'views/purchases_menu.xml',
        'views/product_purchaserinfo_form_view.xml',
        'report/report_account_receivable.xml',
        'report/report_invoice.xml',
        'report/report_packing_list.xml',
        'report/report_pro_forma_invoice.xml',
        'report/report_views.xml',
        ],
}

