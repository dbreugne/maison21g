from odoo import models, fields, api


class InvoiceOrderTeamtWizard(models.TransientModel):
    """Create a new wizard invoice.order.xlsx"""
    _name = 'invoice.order.xlsx'
    _description = 'Wizard to generate the Invoice Order Report'

    date_start = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)
    number = fields.Many2many('account.move','account_rep_rel','view_rep','fin_id','Number')

    def get_report(self):
        data = {'date_start': self.date_start, 'date_end': self.date_end,'number': self.number.ids}
        return self.env.ref('zt_invoice_report.invoice_order_xlsx').report_action(self, data=data)





