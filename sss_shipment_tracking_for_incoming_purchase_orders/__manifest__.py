# -*- coding: utf-8 -*-
# Part of Linserv. See LICENSE file for full copyright and licensing details.

{
    'name': 'sss shipment tracking for incoming purchase_orders',
    'description': """sss_shipment_tracking_for_incoming_purchase_orders""",
    'category': 'Purchase',
    'version': '13.0.2',
    'author': 'Linserv Aktiebolag',
    'website': 'https://www.linserv.se',
    'summary': '',
    'depends': ['purchase', 'report_xlsx', 'mail', 'contacts', 'base'],
    'data': [
        'views/purchase_scheduler_action_view.xml',
        'data/purchase_orders_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
