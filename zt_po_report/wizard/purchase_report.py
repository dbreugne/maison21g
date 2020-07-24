from odoo import models, fields, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderXls(models.AbstractModel):
    _name = 'report.zt_po_report.purchase_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        start_date = data['date_start']
        end_date = data['date_end']
        domain=[]
        if start_date:
            domain.append(('date_order', '>=', start_date))
        if end_date:
            domain.append(('date_order', '<=', end_date))
        purchase_orders = self.env['purchase.order'].sudo().search(domain)
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_align('center')
        cell_format = workbook.add_format({'font_size': '12px'})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        txt = workbook.add_format({'font_size': '10px'})
        irow = 5
        icol = 0
        sheet.merge_range(irow, icol, irow + 2, icol + 13, 'PURCHASE ORDER REPORT DETAILS', format1)
        sheet.write('B2', 'From:', cell_format)
        sheet.merge_range('C2:D2', data['date_start'], txt)
        sheet.write('E2', 'To:', cell_format)
        sheet.merge_range('F2:G2', data['date_end'], txt)
        sl = 1
        xls_date_format = workbook.add_format({'num_format': 'dd-mm-yy hh:mm'})
        sheet.write('B9', 'Number', table_head)
        sheet.write('C9', 'Refernce (PO)', table_head)
        sheet.write('D9', 'Order Date', table_head)
        sheet.write('E9', 'Vendor Name ', table_head)
        sheet.write('F9', 'Vendor Document Reference', table_head)
        sheet.write('G9', 'Product ID', table_head)
        sheet.write('H9', 'Quantity', table_head)
        sheet.write('I9', 'Product Description', table_head)
        sheet.write('J9', 'Received Quantity', table_head)
        sheet.write('K9', 'Balance Quantity To Receive', table_head)
        sheet.write('L9', 'Unit of Measurement', table_head)
        sheet.write('M9', 'Packaging', table_head)
        sheet.write('N9', 'ETD Supplier', table_head)
        sheet.write('O9', 'Tracking Info', table_head)
        sheet.write('P9', 'ETA', table_head)
        sheet.write('Q9', 'Invoicing Status', table_head)
        num = 10
        sl = 1
        for order in purchase_orders:
            sheet.write('B' + str(num), sl, table_head)
            for pro in order.order_line:
                sheet.write('C' + str(num), order.name, cell_format)
                sheet.write('D' + str(num),
                            order.date_order.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if order.date_order else ' ',
                            cell_format)
                sheet.write('E' + str(num), order.partner_id.name if order.partner_id.name else ' ', cell_format)
                sheet.write('F' + str(num), order.partner_ref if order.partner_id else ' ', cell_format)
                package_ids=pro.product_id.packaging_ids
                balance_qty=pro.product_qty-pro.qty_received
                sheet.write('G' + str(num), pro.product_id.product_tmpl_id.name, cell_format)
                sheet.write('H' + str(num), pro.product_qty, cell_format)
                sheet.write('I' + str(num), pro.product_id.name, cell_format)
                sheet.write('J' + str(num), pro.qty_received, cell_format)
                sheet.write('K' + str(num), balance_qty, cell_format)
                sheet.write('L' + str(num), pro.product_uom.name, cell_format)
                sheet.write('M' + str(num), package_ids[:1].name if package_ids[:1].name else '', cell_format)
                sheet.write('N' + str(num), order.x_studio_supplier_etd, cell_format)
                sheet.write('O' + str(num), order.x_studio_tracking_info, cell_format)
                sheet.write('P' + str(num), order.x_studio_eta, cell_format)
                sheet.write('Q' + str(num), order.invoice_status, cell_format)
                num = num + 1
            num = num + 2
            sl = sl + 1
        workbook.close()
