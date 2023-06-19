from odoo import models,fields,api

class PartnerXlsx(models.AbstractModel):
    _name = 'report.excel_pos_report.pos_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Pos Orded XLSX'

    def generate_xlsx_report(self, workbook, data, partners):

        start_date = data['date_start']
        end_date = data['date_end']

        pos_orders = self.env['pos.order'].search([('date_order','>=',start_date),('date_order','<=',end_date)])

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

        sheet.merge_range('C2:J3', 'Pos Order Detail Report ', head)

        sheet.write('C6', 'From:', cell_format)

        sheet.merge_range('D6:E6', data['date_start'], txt)

        sheet.write('F6', 'To:', cell_format)

        sheet.merge_range('G6:H6', data['date_end'], txt)

        sl = 1

        sheet.write('A9', 'Order ID', table_head)
        sheet.write('B9', 'Cashier', table_head)
        sheet.write('C9', 'Order Date', table_head)
        sheet.write('D9', 'Customer Email ', table_head)
        sheet.write('E9', 'Customer Name', table_head)
        sheet.write('F9', 'Product', table_head)
        sheet.write('G9', 'Quantity', table_head)
        sheet.write('H9', 'Product Type', table_head)
        sheet.write('I9', 'Gross Amount', table_head)
        sheet.write('J9', 'Fees', table_head)
        sheet.write('K9', 'Total Amount', table_head)
        sheet.write('L9', 'Discount', table_head)
        sheet.write('M9', 'Net Amount', table_head)
        sheet.write('N9', 'Currency', table_head)
        sheet.write('O9', 'Origin oxf Customer', table_head)
        sheet.write('P9', 'Payment Type', table_head)
        num =10
        sl =1
        format5 = workbook.add_format({'num_format': 'dd/mm/yy hh:mm'})
        # worksheet.write('A5', number, format5)  # 28/02/13 12:00

        for order in pos_orders:
            pro_payment_cur = ''
            pro_payment_cur_type = ''
            for pro_payment in order.payment_ids:
                pro_payment_cur=pro_payment.currency_id.name
                pro_payment_cur_type=pro_payment.payment_method_id.name
            for pro in order.lines:
                sheet.write('A' + str(num), order and order.name or '', cell_format)
                sheet.write('B' + str(num), order.user_id and order.user_id.name or '', cell_format)
                sheet.write('C' + str(num), order.date_order if order.date_order else ' ', format5)
                sheet.write('D' + str(num), order.partner_id.email if order.partner_id.email else ' ', cell_format)
                sheet.write('E' + str(num), order.partner_id.name if order.partner_id else ' ', cell_format)
                sheet.write('F' + str(num),pro.product_id.product_tmpl_id.name or '', cell_format)
                sheet.write('G' + str(num), pro.qty or '', cell_format)
                sheet.write('H' + str(num),pro.product_id.categ_id.name or '', cell_format)
                sheet.write('I' + str(num), pro.price_unit or '', cell_format)
                sheet.write('J' + str(num), pro.tax_ids_after_fiscal_position.name or '', cell_format)
                sheet.write('K' + str(num), pro.price_subtotal or '', cell_format)
                sheet.write('L' + str(num), pro.discount or '', cell_format)
                sheet.write('M' + str(num), pro.price_subtotal or '', cell_format)
                sheet.write('N' + str(num), pro_payment_cur or '', cell_format)
                sheet.write('O' + str(num), order.note if order.note else ' ', cell_format)
                sheet.write('P' + str(num), pro_payment_cur_type or '', cell_format)
                num = num+1
            sl= sl+1
        workbook.close()