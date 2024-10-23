
{
    'name': 'POS Line Section', 
    'version': '17.0.0.0',
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
    'depends': ['base','point_of_sale'],
    'data': [
        'data/data.xml',
        'views/pos_models.xml',
    ],
    
    'assets': {
        'point_of_sale._assets_pos': [
            'dev_pos_line_section/static/src/js/Orderline.js',
            'dev_pos_line_section/static/src/js/SectionButton.js',
            'dev_pos_line_section/static/src/js/WildCardPopup.js',
            'dev_pos_line_section/static/src/xml/**/*',
        ],
    },

    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
