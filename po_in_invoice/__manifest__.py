
{
    'name': 'Invoice And Tax Report',
    'version': '17.0.1.0',
    'sequence': 1,
    'category': '',
    'description':
        """
    """,
    'summary': '',
    'author': 'ZT-DEV',
    'depends': ['sale_management','account', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/sale_order.xml',
        'wizard/invoice_print_wizard_view.xml',
        'views/invoice_template_modification.xml'
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
