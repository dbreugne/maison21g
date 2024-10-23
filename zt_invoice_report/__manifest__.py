
{

    "name": "Invoice xlsx Report",
    "summary": "Invoice xlsx report",
    "version": '17.0.0.0',
    "sequence": 10,
    "author": "ZT-DEV",
    'summary': 'Analyse Your Sales And CRM Performance',
    "license": "OPL-1",
    "depends":
        ['account','report_xlsx'],
    "data":
        [
            'security/ir.model.access.csv',
            'views/invoice_order_wizard_view.xml',
            'report/report_xls.xml'
        ],
    "installable": True,
    "application": True,

}
