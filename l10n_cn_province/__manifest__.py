# -*- encoding: utf-8 -*-
{
    'name': "China - Province",
    'version': '1.0',
    'category': 'Localization',
    'summary': 'Multi-language Localization',
    'description': """  
Localization of People's Republic of China\n
Data established based upon ISO 3166-2:CN\n
Names and record IDs are written in English before translation.\n
Translation may follow language/local convention.\n
This module only includes provincial level administrative regions, including\n
	1. Provinces\n
	2. Municipalities\n
	3. Autonomous Regions\n
	4. Special Administrative Regions\n
	\n
    """,
    'author': 'Cayprol',
    "depends" : ['base'],
    'data': ['data/china_provinces.xml',
             ],
    "images": [],
    'license': 'LGPL-3',
    'qweb': [
            ],  
    
    'installable': True,
}
