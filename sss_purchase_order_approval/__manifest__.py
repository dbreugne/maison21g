# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SSS PURCHASE ORDER APPROVAL',
    'version': '0.1',
    'sequence': 1,
    'category': 'Purchase Order Approval',
    'description': 
        """ 
        Purchase Order Approval
    """,
    'summary': 'Purchase Order Approval',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['purchase', 'report_xlsx', 'base'],
    'data': [ 
        'data/po_first_approval_mail.xml',
        'data/po_second_approval_pending.xml',
        'views/purchase_order_approval_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
