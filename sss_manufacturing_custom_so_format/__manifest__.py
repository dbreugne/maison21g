# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Manufacturing Order Report',
    'version': '0.12',
    'sequence': 1,
    'category': 'Manufacturing Order Report',
    'description': 
        """ 
        Manufacturing Order Report.
    """,
    'summary': 'Manufacturing Order Report',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['mrp', 'sale', 'stock'],
    'data': [
        'report/mo_inherit_report.xml',
        'data/sequence_lot_mrp.xml',
        'views/sale_order_inherit.xml',
        'views/mo_inherit_sale.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
