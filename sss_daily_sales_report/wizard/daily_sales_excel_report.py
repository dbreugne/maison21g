from odoo import models, fields, api, _
import io
from datetime import datetime
import xlsxwriter
import datetime
from base64 import b64encode


class DailySaleReport(models.TransientModel):
    _name = "daily.sale.report"
    _description = "Daily Sale Report"

    file = fields.Binary()
    document = fields.Binary('Excel Report')
    myfile = fields.Char('Excel File', size=64)
    date = fields.Date('Date', default=lambda self: fields.Date.context_today(self), required=True)
    config_id = fields.Many2one('pos.config', 'Point Of Sale')

    def daily_sales_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {})
        worksheet = workbook.add_worksheet("Daily Sale Report")

        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px',  'border': 1})
        data_border_format = workbook.add_format({'align': 'left', 'border': 1})
        data_border_format_right = workbook.add_format({'align': 'right', 'border': 1})
        worksheet.merge_range('A1:H1', 'POS Name', head)
        worksheet.write(1, 0, 'Date', head)
        format5 = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        worksheet.write(1, 1, self.date, format5)

        worksheet.write(3, 0, 'S no', head,)
        worksheet.write_string(3, 1, 'Session no.', head)
        worksheet.write_string(3, 2, 'Receipt no.', head)
        worksheet.write(3, 3, 'Sale amount', head)
        worksheet.write(3, 4, 'GST', head)
        worksheet.write(3, 5, 'Net amount', head)
        worksheet.write(3, 6, 'Payment mode', head)
        worksheet.write(3, 7, 'Sales person', head)

        start_date = datetime.datetime.strptime(str(self.date) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.strptime(str(self.date) + " 23:59:59", "%Y-%m-%d %H:%M:%S")
        domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date)]
        if self.config_id:
            domain.append(('config_id', '=', self.config_id.id))
        pos_order_ids = self.env['pos.order'].search(domain)

        row = 4
        indexing = 1
        counter = 0
        sale_order_count = []
        for rec in pos_order_ids:
            if not rec.session_id.user_id.id in sale_order_count:
                sale_order_count.append(rec.session_id.user_id.id)
            worksheet.write(row, 0, indexing, data_border_format)
            worksheet.write(row, 1, rec.session_id.name, data_border_format)
            worksheet.write(row, 2, rec.name, data_border_format)
            worksheet.write(row, 3, rec.amount_total, data_border_format_right)
            # worksheet.write(row, 4, rec.lines.tax_ids_after_fiscal_position.name, data_border_format)
            worksheet.write(row, 4, [tax.name for tax in rec.lines.tax_ids_after_fiscal_position][0], data_border_format)
            worksheet.write(row, 5, rec.amount_tax, data_border_format_right)
            # worksheet.write(row, 6, rec.payment_ids.payment_method_id.name, data_border_format)
            worksheet.write(row, 6, str(tuple([payment.payment_method_id.name for payment in rec.payment_ids])) if len(rec.payment_ids.ids) > 1 else rec.payment_ids.payment_method_id.name, data_border_format)
            worksheet.write(row, 7, rec.employee_id.name, data_border_format)
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 18)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 18)
            worksheet.set_column('F:F', 12)
            worksheet.set_column('G:G', 15)
            worksheet.set_column('H:H', 18)
            row += 1
            indexing = indexing+1
            counter += 1

        worksheet.merge_range(row+1, 0, row+1, 1, 'Payment summary', head)
        worksheet.write(row+2, 0, 'Cash', data_border_format)
        worksheet.write(row+3, 0, 'Amex', data_border_format)
        worksheet.write(row+4, 0, 'Other Credit card', data_border_format)
        worksheet.write(row+5, 0, 'Alipay/Grabpay/Wechatpay', data_border_format)
        worksheet.write(row+6, 0, 'Simplybookme', data_border_format)
        worksheet.write(row+7, 0, 'Klook', data_border_format)
        worksheet.write(row+8, 0, 'Tipalti', data_border_format)
        worksheet.write(row+9, 0, 'Atome', data_border_format)

        cash_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "Cash").mapped("amount"))
        amex_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "AMEX").mapped("amount"))
        credit_card_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "Credit Card").mapped("amount"))
        simplybookme_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "Simplybook Me").mapped("amount"))
        klook_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "Klook").mapped("amount"))
        tipalti_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "Tipalti").mapped("amount"))
        atome_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "ATOME").mapped("amount"))
        alipay_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "ALIPAY").mapped("amount"))
        grabpay_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "GrabPay").mapped("amount"))
        weChat_pay_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "WeChat Pay").mapped("amount"))
        visamaster_total = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id.name == "Visa/Master").mapped("amount"))
        alipay_grappay_wechat_pay_total = alipay_total + grabpay_total + weChat_pay_total
        # sale_for_today = alipay_grappay_wechat_pay_total + cash_total + amex_total + credit_card_total + simplybookme_total + klook_total + tipalti_total + atome_total
        sale_for_today = sum(pos_order_ids.payment_ids.filtered(lambda x: x.payment_method_id).mapped("amount"))
        
        worksheet.write(row+2, 1, cash_total, data_border_format_right)
        worksheet.write(row+3, 1, amex_total, data_border_format_right)
        worksheet.write(row+4, 1, credit_card_total, data_border_format_right)
        worksheet.write(row+5, 1, alipay_grappay_wechat_pay_total, data_border_format_right)
        worksheet.write(row+6, 1, simplybookme_total, data_border_format_right)
        worksheet.write(row+7, 1, klook_total, data_border_format_right)
        worksheet.write(row+8, 1, tipalti_total, data_border_format_right)
        worksheet.write(row+9, 1, atome_total, data_border_format_right)

        worksheet.merge_range(row+1, 3, row+1, 4, 'End Day Summary Statement', head)
        worksheet.write(row+2, 3, 'Sales for today', data_border_format)
        worksheet.write(row+3, 3, 'Transactions', data_border_format)
        worksheet.write(row+4, 3, 'Quantity', data_border_format)
        worksheet.write(row+5, 3, 'Visa/Master', data_border_format)
        worksheet.write(row+6, 3, 'Amex', data_border_format)
        worksheet.write(row+7, 3, 'Cash', data_border_format)

        qty_total = sum(pos_order_ids.lines.filtered(lambda x: x.qty).mapped("qty"))

        worksheet.write(row+2, 4, sale_for_today, data_border_format_right)
        worksheet.write(row+3, 4, counter, data_border_format_right)
        worksheet.write(row+4, 4, qty_total, data_border_format_right)
        worksheet.write(row+5, 4, visamaster_total, data_border_format_right)
        worksheet.write(row+6, 4, amex_total, data_border_format_right)
        worksheet.write(row+7, 4, cash_total, data_border_format_right)
        row += 8 
        for person in sale_order_count:
            worksheet.write(row, 3, self.env["res.users"].browse(person).name, data_border_format)
            worksheet.write(row, 4, (len(pos_order_ids.filtered(lambda x: x.session_id.user_id.id == person))), data_border_format_right)
            worksheet.write(row, 5, 'Transaction', data_border_format)
            worksheet.write(row, 6, 'Qty', data_border_format)
            worksheet.write(row, 7, (sum(pos_order_ids.filtered(lambda x: x.session_id.user_id.id == person).lines.mapped("qty"))), data_border_format_right)
            row += 1

        workbook.close()
        output.seek(0)
        self.document = b64encode(output.read())
        output.close()

        url = "/web/content/?model=daily.sale.report&field=document&id=%s&filename=%s&download=true" % (self.id, "Daily Sale Report.xlsx")
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
