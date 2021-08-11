
{
    "name": "GDrive POS Export",
    "summary": "GDrive POS Export",
    "author": "ERPITS",
    "license": "AGPL-3",
    "depends": ['sale','base','point_of_sale','report_xlsx', 'google_drive'],
    "data": [
             'views/pos_backup_view.xml',
             'security/ir.model.access.csv'],
    "installable": True,
}
