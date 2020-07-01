from odoo import models, fields, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class CRMTeamXlsx(models.AbstractModel):
    _name = 'report.zt_sales_report.crm_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        start_date = data['date_start']
        end_date = data['date_end']
        sales_team_id = data['team_sales_id']
        crm_team_obj=self.env['crm.team'].browse(sales_team_id)
        domain=[]
        if start_date:
            domain.append(('create_date', '>=', start_date))
        if end_date:
            domain.append(('create_date', '<=', end_date))
        if sales_team_id:
            domain.append(('team_id','=',crm_team_obj.id))
        sale_orders = self.env['crm.lead'].sudo().search(domain)
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_align('center')
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '12px'})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        txt = workbook.add_format({'font_size': '10px'})
        irow = 5
        icol = 0
        sheet.merge_range(irow, icol, irow + 2, icol + 13, 'CRM - SALES TEAM CATEGORIES DETAILS', format1)
        sheet.write('B2', 'From:', cell_format)
        sheet.merge_range('C2:D2', data['date_start'], txt)
        sheet.write('E2', 'To:', cell_format)
        sheet.merge_range('F2:G2', data['date_end'], txt)
        sheet.write('H2', 'Sales By:', cell_format)
        sheet.merge_range('I2:J2',  crm_team_obj.name if crm_team_obj.name else '' , txt)
        sl = 1
        xls_date_format = workbook.add_format({'num_format': 'dd-mm-yy hh:mm'})
        sheet.write('B9', 'Company Name', table_head)
        sheet.write('C9', 'Status', table_head)
        sheet.write('D9', 'Value', table_head)
        sheet.write('E9', 'Sales Person', table_head)
        sheet.write('F9', 'Industry', table_head)
        sheet.write('G9', 'Category', table_head)
        num = 10
        sl = 1
        for order in sale_orders:
            sheet.write('B' + str(num), order.partner_name, table_head)
            sheet.write('C' + str(num), order.stage_id.name, cell_format)
            sheet.write('D' + str(num), order.planned_revenue, cell_format)
            sheet.write('E' + str(num), order.user_id.name if order.partner_id.email else ' ', cell_format)
            sheet.write('F' + str(num), dict(order._fields['industry'].selection).get(order.industry) if order.industry else ' ' , cell_format)
            sheet.write('G' + str(num), dict(order._fields['category'].selection).get(order.category) if order.category else ' ', cell_format)
            num = num + 2
            sl = sl + 1
        workbook.close()
