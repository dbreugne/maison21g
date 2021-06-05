
{

    "name": "Invoice xlsx Report",
    "summary": "Invoice xlsx report",
    "version": '13.0.0.0.0',
    "sequence": 10,
    "author": "ZT-DEV",
    'summary': 'Analyse Your Sales And CRM Performance',
    "license": "AGPL-3",
    "depends":
        ['account','report_xlsx'],
    "data":
        ['views/invoice_order_wizard_view.xml',
         'report/report_xls.xml'],
    "installable": True,
    "application": True,

}
