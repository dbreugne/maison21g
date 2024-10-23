
{
    'name': 'Auto Ganrate Lot No in Shipment', 
    'version': '1.5',
    'sequence': 1, 
    'category': 'Auto Ganrate Lot No In Shipment', 
    'description': 
        """ 
        Auto Ganrate Lot No In Shipment.
    """,
    'summary': 'Auto Ganrate Lot No In Shipment',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['account', 'account_reports', 'web', 'purchase'],
    'data': [
        'views/product_template_inherit.xml',
        'data/sequence_lot_searial.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
    
}
