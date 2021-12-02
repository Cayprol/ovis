{
    'name': 'OVIS',
    'version': '1.15',
    'category': 'Other',
    'description': 'Custom module for OVIS',
    'author': 'Cayprol',
    'depends': [
        'confirm_popup',
        'contacts_enhanced_view',
        'ovis_coa',
        'purchase_supplierinfo_view',
        'sale',
        'sale_enhanced_view',
        ],
    'data': [
        'views/sale_views.xml',
        'views/res_config_settings_views.xml',
        'data/uom.category.csv',
        'data/uom.uom.csv',
            ],
    'assets': {
        'web.assets_backend': [
            'ovis/static/src/legacy/scss/form_view.scss',
        ]
    },
    'license': 'AGPL-3', 
    'installable': True,
    'application'   : True,
    'auto_install'  : False,
}