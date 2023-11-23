{
    'name': 'SSS Sale In Report',
    'description': """sss_sale_in_report""",
    'version': '13.1',
    'summary': 'sss sale in report',
    'author': 'Spellbound Soft Solution',
    'website': 'http://spellboundss.com',
    'depends': ['point_of_sale','account','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_in_report_view.xml',
        # 'report/sale_report_view.xml'
       
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
