# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'BOM Excel Report',
    'version': '0.1',
    'sequence': 1,
    'category': 'BOM Excel Report',
    'description': 
        """ 
        BOM Excel Report.
    """,
    'summary': 'BOM Excel Report',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['account','sale','mrp', 'report_xlsx'],
    'data': [
        # 'security/ir.model.access.csv',
        'report/bom_excel_report_action.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
    
}
