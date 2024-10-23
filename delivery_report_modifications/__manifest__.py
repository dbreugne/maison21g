# -*- coding: utf-8 -*-
{
    'name': 'ZT Delivery Report Modification',
    'version': '17.0.0.0',
    'summary': 'Delivery Report Modification',
    'description': """
        Delivery Report Modification 
    """,
    'depends': [
        'base','stock', 'purchase', 'sale'],
    'data': [
        'views/delivery_report.xml',
        'views/delivery_picking_view.xml',
        'views/delivery_button_print_report.xml',
        'views/layouts.xml'

      
    ]
}
