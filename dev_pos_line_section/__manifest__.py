
{
    'name': 'POS Line Section', 
    'version': '13.0.1.1',
    'sequence': 1, 
    'category': 'Point Of Sale', 
    'description': 
        """ 
        Add section in POS cart.
        Print receipt based on section.
    """,
    'summary': 'Add Section in POS Cart.',
    'author': 'De ',
    'website': 'http://www.de.com',
    'depends': ['point_of_sale'],
    'data': [
        'data/data.xml',
        'views/pos_models.xml',
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
