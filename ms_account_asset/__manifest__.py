{
    'name': "Maison - Account Asset",
    'summary': "Customization in account asset",
    'version': '17.0.1.0.0',
    'description': """
        v 1.0.0 (mfm) \n
        - adding asset info (owner, SN, location)
    """,
    'author': "Portcities",
    'website': "http://portcities.net",
    'category': 'Accounting',
    'depends': ['account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        'views/asset_location_views.xml',
    ],
    'installable': True,
    'application': False,
    "license": "LGPL-3",
    
}
