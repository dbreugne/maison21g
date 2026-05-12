{
    'name': 'Tax by Country (SG/International)',
    'version': '17.0.3.0',
    'category': 'Accounting',
    'summary': 'Auto-apply Sales Tax 9% SR for Singapore, Sales Tax 0% ZR for international orders',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/fix_ecom_invoice_tax_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}