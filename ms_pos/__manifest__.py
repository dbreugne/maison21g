{
    'name': "Maison - POS",
    'summary': "Customization in POS",
    'version': '13.0.1.0.0',
    'description': """
        v 1.0.0 (mfm) \n
        - Add parent category in pos order report \n
    """,
    'author': "Portcities",
    'website': "http://portcities.net",
    'category': 'Sales/Point Of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'reports/pos_order_report.xml',
    ],
    'installable': True,
    'application': False,
}
