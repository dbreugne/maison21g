{
    'name': "Maison - Contacts",
    'summary': "Customization in contact",
    'version': '17.0.1.0.0',
    'description': """
        v 1.0.0 (mfm) \n
        - Change field label of industry on sale report and contact form \n
        - Change action name of menu 'Sectors of Activity' \n 
    """,
    'author': "Portcities",
    'website': "http://portcities.net",
    'category': 'Sale',
    'depends': ['sale', 'base', 'contacts','sale_subscription'],
    'data': [
        'views/res_partner_industry_views.xml',
        'reports/sale_report_views.xml',
    ],
    'installable': True,
    'application': False,
}
