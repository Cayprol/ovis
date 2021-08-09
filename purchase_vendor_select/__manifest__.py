# -*- coding: utf-8 -*-
{
    'name': 'Smart Vendor Select',
    'summary': 'Conditionally select vendor offers',
    'description': """
Select the cheapest supplier info taking the following into account.\n
1. Multi-currency pricing\n
2. Minimum order quantity\n
3. Leadtime\n
4. Sequance of record (manual adjustable in Web UI)\n
5. ID of record (not adjustable, ID is set on creation/import)\n
Filter out vendor offers which MoQ larger than demand quantity.\n
Filter out vendor offers which date are invalid.
""",
    'version': '13.0.0',
    'category': 'Operations/Purchase',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['product', 'purchase'], 
    'data': [
        'views/product_views.xml',
        ],
    'demo': [],
    'test': [],
}
