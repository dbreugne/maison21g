{
    'name': "Maison - Sale Stock",
    'summary': "Customization in Sale and Stock",
    'version': '17.0.1.0.0',
    'description': """
        v 1.0.0 (godelivadiva) \n
        - Sale coupon report \n
        - Available qty on stock quant \n
    """,
    'author': "Portcities",
    'website': "http://portcities.net",
    'category': 'Sales',
    'depends': ['stock', 'sale'],
    'data': [
        'views/stock_picking_views.xml',
        'views/sale_order_views.xml',
        'views/stock_quant_views.xml'
    ],
    'installable': True,
    'application': False,
}
