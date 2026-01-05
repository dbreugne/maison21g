{
    "name": "INOM Account Type",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "summary": "Add custom account types in Chart of Accounts",
    "description": "Adds additional options in the account_type field of Chart of Accounts in Odoo 17.",
    "author": "INOM",
    "depends": ["account"],
    "data": [],
    'assets': {
        'web.assets_backend': [
            'inom_account_type/static/src/js/account_selectable_inherit.js',
            
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
