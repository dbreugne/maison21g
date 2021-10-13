from datetime import datetime

import pytz
from odoo import models, fields, api


class PoProductReportWizard(models.TransientModel):
    _name = 'po.order.product.xlsx'

    apply_date = fields.Boolean("Apply Date")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    products = fields.Many2many('product.product', string="Products")

    def get_report(self):
        date_start = None
        date_end = None
        if self.apply_date:
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
            date_start = pytz.utc.localize(fields.Datetime.from_string(self.date_start)).astimezone(user_tz)
            date_end = pytz.utc.localize(fields.Datetime.from_string(self.date_end)).astimezone(user_tz)
        data = {'date_start': date_start and date_start.replace(hour=00, minute=00),
                'date_end': date_end and date_end.replace(hour=23, minute=59, second=59), "products": self.products.ids,
                "apply_date": self.apply_date}
        return self.env.ref('excel_po_report.po_order_product_xlsx').report_action(self, data=data)





