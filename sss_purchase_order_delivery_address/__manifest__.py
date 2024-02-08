# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SSS Purchase Order Devilery Address',
    'version': '0.2',
    'sequence': 1,
    'category': 'Purchase Order Devilery Address',
    'description': 
        """ 
        Purchase Order Devilery Address.
    """,
    'summary': 'Purchase Order Devilery Address',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['purchase', 'purchase_stock', 'sale'],
    'data': [ 
        'views/purchase_order_delivery_address_view.xml',
        'report/purchase_order_delivery_address_template_inherit.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
