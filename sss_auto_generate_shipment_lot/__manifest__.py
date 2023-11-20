# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Auto Ganrate Lot No in Shipment',
    'version': '1.6',
    'sequence': 1,
    'category': 'Auto Ganrate Lot No In Shipment',
    'description':
        """
        Auto Ganrate Lot No In Shipment.
    """,
    'summary': 'Auto Ganrate Lot No In Shipment',
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
