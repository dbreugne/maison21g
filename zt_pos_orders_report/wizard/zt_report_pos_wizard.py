from collections import defaultdict

import xlsxwriter
import base64
from odoo import fields, models, api
from io import BytesIO
from datetime import datetime
from pytz import timezone
import pytz
import logging

_logger = logging.getLogger(__name__)

class ZtReportPos(models.TransientModel):
    _name = "zt.report.pos"
    _description = "Pos Report .xlsx"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def print_excel_report(self):
        domain = []
        if self.from_date:
            domain.append(("date_order", ">=", self.from_date))
        if self.to_date:
            domain.append(("date_order", "<=", self.to_date))
        records = self.env["pos.order"].search(domain)
        report_name = 'POS Report'
        filename = '%s' % report_name

        columns = [
            ('No', 5, 'no', 'no'),
            ('Internal Notes', 30, 'char', 'char'),
            ('Order Ref', 30, 'char', 'char'),
            ('Session', 20, 'char', 'char'),
            ('Date', 20, 'datetime', 'char'),
            ('Receipt Number', 20, 'char', 'char'),
            ('Customer', 20, 'char', 'char'),
            ('Email', 30, 'char', 'char'),
            ('Cashier', 20, 'char', 'char'),
            ('Total', 30, 'float', 'float'),
            ('Order Lines/Product', 20, 'char', 'char'),
            ('Product Combination', 20, 'char', 'char'),
            ('Order Lines/Quantity', 20, 'float', 'float'),
            ('Order Lines Created On', 20, 'datetime', 'char'),
            ('Order Lines/Unit Price', 20, 'float', 'float'),
            ('Order Lines/Currency', 20, 'char', 'char'),
            ('Customer/Name', 30, 'char', 'char'),
            ('Order Lines/Name', 20, 'char', 'char'),
        ]

        datetime_format = '%Y-%m-%d %H:%M:%S'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)

        worksheet = workbook.add_worksheet(report_name)
        # worksheet.merge_range('A2:I4', report_name, wbf['title_doc'])

        row = 1

        col = 0
        for column in columns:
            column_name = column[0]
            column_width = column[1]
            column_type = column[2]
            worksheet.set_column(col, col, column_width)
            worksheet.write(row - 1, col, column_name, wbf['header_orange'])

            col += 1

        row += 1
        row1 = row
        no = 1

        column_float_number = {}
        result_dict_list = []
        for order_line in records:
            # data = {
            #     "internal_notes": order_line.note,
            #     "order_ref": order_line.name,
            #     "session": order_line.session_id.name,
            #     "date": order_line.date_order,
            #     "receipt_number": order_line.pos_reference,
            #     "customer": order_line.partner_id.name,
            #     "email": order_line.partner_id.email,
            #     "cashier": order_line.user_id.name,
            #     "total": order_line.amount_total,
            # }
            new_column_data = defaultdict(list)
            combination_column_data = defaultdict(list)
            col_index = False
            order_data_list = []
            for index, lines in enumerate(order_line.lines, start=1):
                if not lines.product_id:
                    col_index = index
                if col_index and lines.product_id:
                    combination_column_data[col_index] += [lines.product_id.name]
                if lines.product_id.is_pos_master:
                    col_index = index
                if col_index and not lines.product_id.is_pos_master:
                    new_column_data[col_index] += [lines.product_id.name]
                if index == 1:
                    data = [order_line.note,
                            order_line.name,
                            order_line.session_id.name,
                            order_line.date_order,
                            order_line.pos_reference,
                            order_line.partner_id.name,
                            order_line.partner_id.email,
                            order_line.user_id.name,
                            order_line.amount_total,
                            lines.product_id.name,
                            "",
                            lines.qty,
                            lines.create_date,
                            lines.price_unit,
                            lines.currency_id.name,
                            order_line.partner_id.name,
                            lines.name ]
                else:
                    data = ["", "", "", "", "", "", "", "", "",

                            lines.product_id.name,
                            "",
                            lines.qty,
                            lines.create_date,
                            lines.price_unit,
                            lines.currency_id.name,
                            order_line.partner_id.name,
                            lines.name]
                order_data_list.append(data)
            for col_idx, col_vals in new_column_data.items():
                join_list = [str(x) for x in col_vals if x]
                order_data_list[col_idx - 1][10] = ", ".join(join_list)
            for col_idx, col_vals in combination_column_data.items():
                join_list = [str(x) for x in col_vals if x]
                order_data_list[col_idx - 1][10] = ", ".join(join_list)
            result_dict_list += order_data_list
        # result = []
        # for items in result_dict_list:
        #     result.append(
        #         [items.get('internal_notes'), items.get('order_ref'), items.get('session'), items.get('date'),
        #          items.get('receipt_number'), items.get('customer'),
        #          items.get('email'), items.get('cashier'), items.get('total'), items.get('order_ines_Product'),
        #          items.get('new_column'), items.get('order_ines_quantity'),
        #          items.get('order_lines_created_on'), items.get('order_lines_unit_price'),
        #          items.get('order_lines_currency'), items.get('customer_name'), items.get('order_ines_name')]
        #     )
        for res in result_dict_list:
            col = 0
            for column in columns:
                column_name = column[0]
                column_width = column[1]
                column_type = column[2]
                if column_type == 'char':
                    col_value = res[col - 1] if res[col - 1] else ''
                    wbf_value = wbf['content']
                elif column_type == 'no':
                    col_value = no
                    wbf_value = wbf['content']
                elif column_type == 'datetime':
                    col_value = res[col - 1].strftime('%Y-%m-%d %H:%M:%S') if res[col - 1] else ''
                    wbf_value = wbf['content']
                else:
                    if type(res[col - 1]) != str:
                        col_value = res[col - 1] if res[col - 1] else 0
                        if column_type == 'float':
                            wbf_value = wbf['content_float']
                        else:  # number
                            wbf_value = wbf['content_number']
                        column_float_number[col] = column_float_number.get(col, 0) + col_value
                    else:
                        col_value = res[col - 1]
                        wbf_value = wbf['content']

                worksheet.write(row - 1, col, col_value, wbf_value)

                col += 1

            row += 1
            no += 1
        workbook.close()
        out = base64.encodebytes(fp.getvalue())
        self.write({'datas': out, 'datas_fname': filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model=' + self._name + '&id=' + str(
                self.id) + '&field=datas&download=true&filename=' + filename,
        }

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFFF',
            'orange': '#FFFFFF',
            'red': '#FFFFFF',
            'yellow': '#FFFFFF',
        }

        wbf = {}
        wbf['header'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['orange'], 'font_color': '#000000',
             'font_name': 'Georgia'})
        wbf['header_orange'].set_border()

        wbf['header_yellow'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['yellow'], 'font_color': '#000000',
             'font_name': 'Georgia'})
        wbf['header_yellow'].set_border()

        wbf['header_no'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')

        wbf['footer'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})

        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'font_name': 'Georgia'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()

        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd', 'font_name': 'Georgia'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()

        wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,
            'font_name': 'Georgia',
        })

        wbf['company'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})
        wbf['company'].set_font_size(11)

        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()

        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()

        wbf['content_percent'] = workbook.add_format({'align': 'right', 'num_format': '0.00%', 'font_name': 'Georgia'})
        wbf['content_percent'].set_right()
        wbf['content_percent'].set_left()

        wbf['total_float'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()

        wbf['total_number'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['white_orange'], 'bold': 1, 'num_format': '#,##0',
             'font_name': 'Georgia'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()

        wbf['total'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()

        wbf['total_number_yellow'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['yellow'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()

        wbf['total_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()

        wbf['total_number_orange'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['orange'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()

        wbf['total_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()

        wbf['header_detail_space'] = workbook.add_format({'font_name': 'Georgia'})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()

        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2', 'font_name': 'Georgia'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()

        return wbf, workbook