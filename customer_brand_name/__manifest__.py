{
    'name': 'Customer Brand Name',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Customer Brand with related users',
    'depends': ['sale', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_brand_views.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
