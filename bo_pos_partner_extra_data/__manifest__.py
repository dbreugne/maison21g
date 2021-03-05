

{
    'name': 'ZT- Pos Partner Doc',
    'summary': 'zt pos data',
    'description': """zt pos data.""",
    'category': 'Point Of Sale',
    'version': '1.0',
    'website': 'http://www.zt.com/',
    'author': 'ZTR',
    'depends': ['point_of_sale', 'bo_partner_extra_data'],
    'data': [
        'views/point_of_sale.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'application': True,
}
