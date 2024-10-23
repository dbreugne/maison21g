# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Task',
    'version': '17.0.1.0',
    'sequence': 1,
    'category': 'Project Task',
    'description':
        """
        Project Task.
    """,
    'summary': 'Project Task',
    'author': 'Spellbound Soft Solutions',
    'website': 'http://spellboundss.com/',
    'depends': ['project'],
    'data': [
        'views/project_task_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
    
}
