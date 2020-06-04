from odoo import models, fields, api


class PartnerXlsx(models.AbstractModel):
    _name = 'report.excel_pos_report.pos_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        start_date = data['date_start']
        end_date = data['date_end']

        pos_orders = self.env['pos.order'].search([('date_order', '>=', start_date), ('date_order', '<=', end_date)])

        # One sheet by partner
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'font_size': '12px'})

        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})

        txt = workbook.add_format({'font_size': '10px'})

        sheet.merge_range('B2:I3', 'Pos Order Detail Report ', head)

        sheet.write('B6', 'From:', cell_format)

        sheet.merge_range('C6:D6', data['date_start'], txt)

        sheet.write('F6', 'To:', cell_format)

        sheet.merge_range('G6:H6', data['date_end'], txt)

        sl = 1
        xls_date_format = workbook.add_format({'num_format': 'dd-mm-yy hh:mm'})

        sheet.write('B9', 'Number', table_head)
        sheet.write('C9', 'Order ID', table_head)
        sheet.write('D9', 'Order Date', table_head)
        sheet.write('E9', 'Customer Email ', table_head)
        sheet.write('F9', 'Customer Name', table_head)
        sheet.write('G9', 'Product', table_head)
        sheet.write('H9', 'Quantity', table_head)
        sheet.write('I9', 'Product Type', table_head)
        sheet.write('J9', 'Gross Amount', table_head)
        sheet.write('K9', 'Fees', table_head)
        sheet.write('L9', 'Total Amount', table_head)
        sheet.write('M9', 'Discount', table_head)
        sheet.write('N9', 'Net Amount', table_head)
        sheet.write('O9', 'Currency', table_head)
        # sheet.write('P9', 'Payment Type', table_head)
        sheet.write('P9', 'Origin of Customer', table_head)
        sheet.write('Q9', 'Payment Type', table_head)
        num = 10
        sl = 1
        for order in pos_orders:
            sheet.write('B' + str(num), sl, table_head)
            sheet.write('C' + str(num), order.name, cell_format)
            sheet.write('D' + str(num), order.date_order if order.date_order else ' ', txt)
            sheet.write('E' + str(num), order.partner_id.email if order.partner_id.email else ' ', cell_format)
            sheet.write('F' + str(num), order.partner_id.name if order.partner_id else ' ', cell_format)
            pro_payment_cur = ''
            pro_payment_cur_type = ''
            for pro_payment in order.payment_ids:
                pro_payment_cur = pro_payment.currency_id.name
                pro_payment_cur_type = pro_payment.payment_method_id.name
            for pro in order.lines:
                sheet.write('G' + str(num), pro.product_id.product_tmpl_id.name, cell_format)
                sheet.write('H' + str(num), pro.qty, cell_format)
                sheet.write('I' + str(num), pro.product_id.categ_id.name, cell_format)
                sheet.write('J' + str(num), pro.price_unit, cell_format)
                sheet.write('K' + str(num), pro.tax_ids_after_fiscal_position.name, cell_format)
                sheet.write('L' + str(num), pro.price_subtotal, cell_format)
                sheet.write('M' + str(num), pro.discount, cell_format)
                sheet.write('N' + str(num), pro.price_subtotal, cell_format)

                # sheet.write('P' + str(num), pro_payment_cur, cell_format)
                num = num + 1
            # sheet.write('Q' + str(num), order.note if order.note else ' ', cell_format)
            sheet.write('O' + str(num), pro_payment_cur, cell_format)
            sheet.write('P' + str(num), order.note if order.note else ' ', cell_format)
            sheet.write('Q' + str(num), pro_payment_cur_type, cell_format)
            num = num + 2
            sl = sl + 1
        workbook.close()
