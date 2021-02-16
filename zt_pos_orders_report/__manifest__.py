
{
    'name': 'POS Order Extraction',
    'version': '13.0.1.1',
    'sequence': 1, 
    'category': 'Point Of Sale', 
    'description': 
        """ 
    """,
    'summary': 'POS Order Extraction',
    'author': 'De ',
    'website': 'http://www.de.com',
    'depends': ['point_of_sale'],
    'data': [
        'wizard/zt_report_pos_wizard.xml',
        'views/product_template.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
