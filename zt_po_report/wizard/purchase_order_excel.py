from odoo import models, fields, api


class PurchaseOrderWizard(models.TransientModel):

    _name = 'purchase.order.xlsx'

    date_start = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)

    def get_report(self):
        data = {'date_start': self.date_start, 'date_end': self.date_end,}
        return self.env.ref('zt_po_report.purchase_order_xlsx').report_action(self, data=data)






