# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

{
    'name': 'POS Orders Reprint',
    'version': '17.0.0.0',
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
    ],
    'demo': [],

    'assets': {
        'point_of_sale._assets_pos': [
            'dev_pos_reprint_orders/static/src/app/screens/product_screen/control_buttons/ShowOrdersButtonWidget/ShowOrdersButtonWidget.js',
            'dev_pos_reprint_orders/static/src/app/screens/product_screen/control_buttons/ShowOrdersButtonWidget/ShowOrdersButtonWidget.xml',
            
            'dev_pos_reprint_orders/static/src/app/screens/product_screen/pos_orders_screen/OrderListScreenWidget.js',
            'dev_pos_reprint_orders/static/src/app/screens/product_screen/pos_orders_screen/OrderListScreenWidget.xml',

            'dev_pos_reprint_orders/static/src/app/screens/product_screen/pos_orders_screen/pos_orders_line.js',
            'dev_pos_reprint_orders/static/src/app/screens/product_screen/pos_orders_screen/pos_orders_line.xml',

            'dev_pos_reprint_orders/static/src/app/screens/receipt_screen/receipt/order_reprint_receipt.js',
            'dev_pos_reprint_orders/static/src/app/screens/receipt_screen/receipt/order_reprint_receipt.xml',

            'dev_pos_reprint_orders/static/src/app/screens/receipt_screen/receipt/order_reprint_screen.js',
            'dev_pos_reprint_orders/static/src/app/screens/receipt_screen/receipt/order_reprint_screen.xml',

            'dev_pos_reprint_orders/static/src/app/models/db.js',
        ],
    },
    
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
