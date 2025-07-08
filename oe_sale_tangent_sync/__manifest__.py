# -*- coding: utf-8 -*-
{
    'name': 'Maison - Tangent API Integration',
    'version': '17.0.1.0',
    'category': 'Sales',
    'summary': 'Integration with Tangent API for POS and Sales',
    'description': """
        This module provides integration with Tangent API for POS and Sales synchronization.
    """,
    'author': 'Odoo Edge',
    'depends': ['base', 'sale', 'point_of_sale'],
    'data': [
        'data/ir_cron_data.xml',
        'data/tangent_api_data.xml',
        'security/ir.model.access.csv',
        'wizard/tangent_sync_date_wizard_views.xml',
        'views/api_log_views.xml',
        'views/api_config_views.xml',
        'views/sale_order_views.xml',
        'views/pos_order_views.xml',
        'views/pos_payment_method_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
