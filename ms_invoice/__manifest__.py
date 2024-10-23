
{
    'name': 'MS: Invoice',
    'version': '17.0.1.0.0',
    'sequence': 1,
    'category': 'Accounting',
    'description': """ 
        Subtotal display in invoice form and report \n
    """,
    'summary': 'Invoices & Payments',
    'author': 'Portcities Ltd',
    'website': 'http://portcities.net',
    'depends': ['account'],
    'data': [
        'reports/account_move_report.xml',
        'views/account_move_views.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
