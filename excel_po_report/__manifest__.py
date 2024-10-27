
{
    "name": "po product xlsx report",
    "summary": "Module to create PO last product xlsx report",
    "license": "AGPL-3",
    "version": '17.0.0.0',
    "author":"ERPITS",
    "website":"consult.erpits.com",
    "depends": ['base','purchase','report_xlsx'],
    "data": ['views/po_product_wizard_view.xml',
             'report/report_xls.xml',
        'security/ir.model.access.csv'],
    "installable": True,
}
