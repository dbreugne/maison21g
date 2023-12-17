# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Vendor Payment Term', 
    'version': '13.0.1',
    'sequence': 1, 
    'category': 'Vendor Payment Term', 
    'description': 
        """ 
        Vendor Payment Term.
    """,
    'summary': 'Vendor Payment Term',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['purchase', 'account'],
    'data': [
        'data/account_payment_term.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
