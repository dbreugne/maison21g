from odoo import models, fields, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class SalesTeamXlsx(models.AbstractModel):
    _name = 'report.zt_sales_report.sale_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        start_date = data['date_start']
        end_date = data['date_end']
        sales_team_id = data['team_sales_id']
        crm_team_obj = self.env['crm.team'].browse(sales_team_id)
        domain=[]
        if start_date:
            domain.append(('date_order', '>=', start_date))
        if end_date:
            domain.append(('date_order', '<=', end_date))
        if sales_team_id:
            domain.append(('team_id','=',sales_team_id))
        sale_orders = self.env['sale.order'].sudo().search(domain)
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_align('center')
        cell_format = workbook.add_format({'font_size': '12px'})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        txt = workbook.add_format({'font_size': '10px'})
        irow = 5
        icol = 0
        sheet.merge_range(irow, icol, irow + 2, icol + 13, 'SALES ORDER REPORT DETAILS', format1)
        sheet.write('B2', 'From:', cell_format)
        sheet.merge_range('C2:D2', data['date_start'], txt)
        sheet.write('E2', 'To:', cell_format)
        sheet.merge_range('F2:G2', data['date_end'], txt)
        sheet.write('H2', 'Sales By:', cell_format)
        sheet.merge_range('I2:J2', crm_team_obj.name, txt)
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
        sheet.write('M9', 'Currency', table_head)
        sheet.write('N9', 'Origin of Customer', table_head)
        sheet.write('O9', 'Payment Delay', table_head)
        sheet.write('P9', 'Order Status', table_head)
        num = 10
        sl = 1
        for order in sale_orders:
            sheet.write('B' + str(num), sl, table_head)
            sheet.write('C' + str(num), order.name, cell_format)
            sheet.write('D' + str(num), order.date_order.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if order.date_order else ' ', cell_format)
            sheet.write('E' + str(num), order.partner_id.email if order.partner_id.email else ' ', cell_format)
            sheet.write('F' + str(num), order.partner_id.name if order.partner_id else ' ', cell_format)
            sheet.write('P' + str(num),
                        dict(order._fields['state'].selection).get(order.state) if order.state else ' ',
                        cell_format)
            sheet.write('O' + str(num), order.payment_term_id.name if order.payment_term_id else ' ', cell_format)

            pro_payment_cur = ''
            for pro in order.order_line:
                sheet.write('G' + str(num), pro.product_id.product_tmpl_id.name, cell_format)
                sheet.write('H' + str(num), pro.product_uom_qty, cell_format)
                sheet.write('I' + str(num), pro.product_id.categ_id.name, cell_format)
                sheet.write('J' + str(num), pro.price_unit, cell_format)
                sheet.write('K' + str(num), pro.tax_id.name, cell_format)
                num = num + 1
            sheet.write('M' + str(num), order.currency_id.name, cell_format)
            sheet.write('N' + str(num), order.partner_id.comment if order.partner_id.comment else ' ', cell_format)
            sheet.write('L' + str(num), order.amount_total, cell_format)
            #
            num = num + 2
            sl = sl + 1
        workbook.close()
