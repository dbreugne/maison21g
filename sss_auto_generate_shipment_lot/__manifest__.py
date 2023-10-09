# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Auto Generate Lot No in Shipment',
    'version': '0.1',
    'sequence': 1,
    'category': 'Auto Generate Lot No In Shipment',
    'description': 
        """ 
        Auto Generate Lot No In Shipment.
    """,
    'summary': 'Auto Generate Lot No In Shipment',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['account', 'account_reports', 'web', 'purchase'],
    'data': [
        'views/product_template_inherit.xml',
        'data/sequence_lot_searial.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
