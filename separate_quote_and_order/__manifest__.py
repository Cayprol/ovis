# -*- coding: utf-8 -*-
{
    'name': 'Separate Quotation & Sale Order',
    'summary': "Separate Quotation & Sale Order sequence and workflow",
    'description': """
This module modifies the standard workflow of Quotation to Sale Order.  
A Sale Order is created based on existing Quotation by creating a new record in database.  
Quotation and Sale Order will have different sequence number.  
    """,
    'version': '12.0.0',
    'category': 'Sales/Sales',
    'author': 'Cayprol',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['sale', 'sale_management'],
    'data': ['data/sequence.xml'],
    'demo': [],
    'test': [],
}
