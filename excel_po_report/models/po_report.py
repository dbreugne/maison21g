from odoo import models, fields, api


class PartnerXlsx(models.AbstractModel):
    _name = 'report.excel_po_report.po_order_product_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        apply_date = data['apply_date']
        start_date = data['date_start']
        end_date = data['date_end']
        products = data['products']
        domain = [('state','=','purchase')]
        if apply_date:
            domain += [('date_order', '>=', start_date), ('date_order', '<=', end_date)]
        if products:
            domain.append(("product_id", "in", products))

        po_lines = self.env['purchase.order.line'].search(domain, order="id DESC")

        # One sheet by partner
        sheet = workbook.add_worksheet()
        sheet.set_column('A:A', 23)
        sheet.set_column('B:B', 23)
        sheet.set_column('C:C', 23)
        sheet.set_column('D:D', 23)
        sheet.set_column('E:E', 23)
        sheet.set_column('F:F', 27)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 10)
        sheet.set_column('M:M', 10)
        sheet.set_column('N:N', 10)
        sheet.set_column('O:O', 10)
        sheet.set_column('P:P', 10)
        cell_format = workbook.add_format({'font_size': '12px'})

        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '11px'})

        txt = workbook.add_format({'font_size': '10px'})

        sl = 1

        sheet.write('A1', 'Internal Reference', table_head)
        sheet.write('B1', 'Name', table_head)
        sheet.write('C1', 'Unit Price', table_head)
        sheet.write('D1', 'Latest PO number', table_head)
        sheet.write('E1', 'Latest PO Date ', table_head)
        sheet.write('F1', 'PO currency', table_head)
        sheet.write('G1', 'Unit Price in SGD', table_head)
        num = 2
        sl = 1
        format5 = workbook.add_format({'num_format': 'dd/mm/yy'})
        # worksheet.write('A5', number, format5)  # 28/02/13 12:00
        product_ids = []
        for order in po_lines:
            if order.product_id not in product_ids:
                product_ids.append(order.product_id)
                currency_sgd = self.env.ref('base.SGD')
                amount_in_sgd = currency_sgd and currency_sgd._convert(order.price_total, order.currency_id, order.company_id, order.date_order, round=True)
                sheet.write('A' + str(num), order.product_id and order.product_id.default_code or '', cell_format)
                sheet.write('B' + str(num), order.product_id and order.product_id.name or '', cell_format)
                sheet.write('C' + str(num), order.product_id and "%0.2f" % order.product_id.list_price or '', cell_format)
                sheet.write('D' + str(num), order.order_id and order.order_id.name or ' ', cell_format)
                sheet.write('E' + str(num), order.date_order or ' ', format5)
                sheet.write('F' + str(num), order.currency_id.name or ' ', cell_format)
                sheet.write('G' + str(num), amount_in_sgd or '', cell_format)
                num = num + 1
                sl = sl + 1
        workbook.close()