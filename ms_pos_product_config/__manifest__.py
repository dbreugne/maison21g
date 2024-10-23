
{
    'name': 'POS Perfume Configurator',
    'version': '17.0.0.0',
    'sequence': 1,
    'category': 'Point Of Sale',
    'description': """ 
        Add Perfume Configurator. \n
        Add Scent selection in sale \n
        move field client_order_ref
    """,
    'summary': 'Add Perfume Configurator.',
    'author': 'Portcities Ltd',
    'website': 'http://portcities.net',
    'depends': ['point_of_sale', 'account', 'sale','dev_pos_line_section'],
    'data': [
        'reports/pos_order_report.xml',
        'data/server_actions_bottle.xml',
        'data/scheduled_actions_bottle.xml',
        'views/product_views.xml',
        #'views/pos_order_line_views.xml',
        'views/sale_order_views.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'ms_pos_product_config/static/src/app/Popup/PerfumeConfiguratorPopup.js',
            'ms_pos_product_config/static/src/app/models/pos_model.js',
            'ms_pos_product_config/static/src/app/xml/Parfume_config_popup.xml',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
