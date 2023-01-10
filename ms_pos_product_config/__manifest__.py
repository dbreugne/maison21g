
{
    'name': 'POS Perfume Configurator', 
    'version': '13.0.1.1',
    'sequence': 1, 
    'category': 'Point Of Sale', 
    'description': """ 
        Add Perfume Configurator.
    """,
    'summary': 'Add Perfume Configurator.',
    'author': 'Portcities Ltd',
    'website': 'http://portcities.net',
    'depends': ['point_of_sale', 'account'],
    'data': [
        'views/template.xml',
        'views/product_views.xml',
    ],
    'qweb': [
        'static/src/xml/parfume_config.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
