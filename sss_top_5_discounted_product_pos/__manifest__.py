# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SSS Top 5 Discounted Product In pos',
    'description': """SSS Top 5 Discounted Product In pos""",
    'version': '0.1',
    'summary': 'SSS Top 5 Discounted Product In pos',
    'author': 'Spellbound Soft Solution',
    'website': 'http://spellboundss.com',
    'depends': ['point_of_sale', 'account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/top_5_product_of_pos_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
