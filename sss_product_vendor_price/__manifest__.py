# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Vendor Price', 
    'version': '13.0.1',
    'sequence': 1, 
    'category': 'Product Vendor Price', 
    'description': 
        """ 
        Product Vendor Price.
    """,
    'summary': 'Product Vendor Price',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['product','sale'],
    'data': [
        'views/product_vendor_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
