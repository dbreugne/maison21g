{
    'name': 'Internal Transfer Email',
    'version': '17.0.0.1',
    'author': '',
    'summary': 'Email Sent on Transfers',
    'category': 'Stock',
    'depends': ['stock'],
    'data': [
        'report/package_transfer_report.xml',
        'data/mail_template.xml',
        'views/stock_email_view.xml',

    ],
    'description': """
       
    """,
    'images': ['static/img/main.png'],
    'auto_install': False,
    'installable': True,
}

