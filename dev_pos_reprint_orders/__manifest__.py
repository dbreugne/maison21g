# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

{
    'name': 'POS Orders Reprint',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Point Of Sale',
    'description':
        """ 
POS Orders Reprint


    """,
    'summary': 'POS Orders Reprint',
    'author': 'ZTR_DEV', 
    'website': 'ztr',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/dev_pos.xml',
        'views/assets.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
