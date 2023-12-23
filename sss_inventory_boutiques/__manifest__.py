# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inventory Boutiques',
    'version': '0.1',
    'sequence': 1,
    'category': 'Inventory Boutiques',
    'description':
        """
        Inventory Boutiques.
    """,
    'summary': 'Inventory Boutiques',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['point_of_sale', 'zt_email_transfer'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_boutiques.xml',
        'views/stock_picking_view.xml',
        # 'views/sale_order_inherit.xml',
        # 'views/mo_inherit_sale.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
