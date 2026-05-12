{
    'name': 'MS: Rollback Invoice Tax (Emergency Fix)',
    'version': '17.0.1.0',
    'category': 'Accounting',
    'summary': 'One-time wizard to rollback invoice tax codes incorrectly overwritten by module update on 2026-05-10',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/rollback_inv_tax_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
