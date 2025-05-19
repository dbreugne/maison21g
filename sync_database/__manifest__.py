{
    'name': 'Database Synchronization',
    'description': """
    """,
    'author': 'Akili Systems (P) Ltd.',
    'version': '1.0',
    'depends': ['sale_management','point_of_sale','stock'],
    'data': [
             'security/ir.model.access.csv',
             'data/booking_sequence.xml',
             'views/order_data_hourly.xml',
             'views/database_server_view.xml',
             'wizard/wizard_message_view.xml',
             'data/sync_record.xml',
            ],
    'installable': True,
    'auto_install': False,
}
