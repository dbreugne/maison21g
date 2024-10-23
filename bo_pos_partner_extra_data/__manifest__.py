{
    'name': 'ZT- Pos Partner Doc',
    'summary': 'zt pos data',
    'description': """zt pos data.""",
    'category': 'Point Of Sale',
    'version': '17.0.0.0',
    'website': 'http://www.zt.com/',
    'author': 'ZTR',
    'depends': ['point_of_sale', 'bo_partner_extra_data'],
    
    'assets': {
        'point_of_sale._assets_pos': [
            'bo_pos_partner_extra_data/static/src/app/pos_partner.js',
            'bo_pos_partner_extra_data/static/src/app/pos_partner.xml',
        ],
    },

    'application': True,
}
