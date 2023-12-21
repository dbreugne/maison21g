# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name': 'SSS DAILY SALES REPORT',
	'version': '0.6',
	'sequence': 1,
	'category': 'Daily Sales Report',
	'description': 
		""" 
		Daily Sales Report.
	""",
	'summary': 'Daily Sales Report',
	'author': 'Spellbound Soft Solutions',
	'website': 'http://spellboundss.com/',
	'depends': ['point_of_sale'],
	'data': [
		'wizard/daily_sales_excel_report_view.xml',
		'security/ir.model.access.csv',
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
