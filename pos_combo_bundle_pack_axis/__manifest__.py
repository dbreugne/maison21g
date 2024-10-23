# -*- coding: utf-8 -*-

{
    'name': 'POS Bundle Product Pack, ',
    'version': '17.0.0.0',
    'category': 'Point of Sale',
    'support': '',
    'author': 'ERPITS',
    'website': 'http://www..com',
    'summary': "Product bundle pack, POS combo pack kit, POS combo pack in odoo, POS bundle product, POS combo products, Add multiple product in pos, sale pos combo product bundle in pos, Combo product sale offer.",
    'description': "Product bundle pack, POS combo pack kit, POS combo pack in odoo, POS bundle product, POS combo products, Add multiple product in pos, sale pos combo product bundle in pos, Combo product sale offer.",
    'images': [
        'static/description/images/pos_combo_logo.png',
    ],
    'depends': [
        'point_of_sale'
    ],

    'data': [
        'security/ir.model.access.csv',
        # 'views/product_combo_assets.xml',
        'views/product_template.xml',
        'views/pack_product.xml',
        # 'views/pos_config.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
    'auto_install': False,
    'currency': 'USD',
    'qweb': ['static/src/xml/pos.xml'],
}
