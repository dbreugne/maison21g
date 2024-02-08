
{
    'name': 'Gernal Ledger Report', 
    'version': '13.0.1.9',
    'sequence': 1, 
    'category': 'Gernal Ledger Report', 
    'description': 
        """ 
        Gernal Ledger Report.
    """,
    'summary': 'Gernal Ledger Report',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['account','account_reports','web'],
    'data': [
        'views/template_search_country.xml',
        'views/assets.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
