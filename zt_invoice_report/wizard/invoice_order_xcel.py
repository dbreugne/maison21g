from odoo import models, fields, api


class InvoiceOrderTeamtWizard(models.TransientModel):
    _name = 'invoice.order.xlsx'

    date_start = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)

    def get_report(self):
        data = {'date_start': self.date_start, 'date_end': self.date_end}
        return self.env.ref('zt_invoice_report.invoice_order_xlsx').report_action(self, data=data)






