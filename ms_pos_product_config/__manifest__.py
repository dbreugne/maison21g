
{
    'name': 'POS Perfume Configurator',
    'version': '13.0.1.3',
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
    'depends': ['point_of_sale', 'account', 'sale'],
    'data': [
        'views/template.xml',
        'reports/pos_order_report.xml',
        'views/product_views.xml',
        'views/pos_order_line_views.xml',
        'views/sale_order_views.xml',
    ],
    'qweb': [
        'static/src/xml/parfume_config.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
