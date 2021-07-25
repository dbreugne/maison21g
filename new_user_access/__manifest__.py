{
    'name': 'Security',
    'version': '14.0.0',
    'category': 'General',
    'summary': 'User Management',
    'description': """
==================================

    """,
    'author': '',
    'website': '',
    'depends': ['base', 'project', 'analytic', 'sale', 'point_of_sale', "stock", "product", "mrp", "account"
        , "purchase", "hide_any_menu"],
    'data': [
        'security/all_security.xml',
        'security/ir.model.access.csv',
        "security/inventory_user_acess.xml",
        "security/purchase_access.xml",
        "security/finance_access.xml",
        "security/outbount.xml"
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
