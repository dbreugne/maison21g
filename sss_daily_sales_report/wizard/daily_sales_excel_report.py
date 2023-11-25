from odoo import models, fields, api, _
import base64
import xlrd
import io
import math
from datetime import datetime, timedelta
import xlsxwriter
import datetime
from base64 import b64decode , b64encode


class DailySaleReport(models.TransientModel):
	_name = "daily.sale.report"
	_description = "Daily Sale Report"  

	file = fields.Binary()
	document = fields.Binary('Excel Report')
	myfile = fields.Char('Excel File', size=64)
	date = fields.Date('Date')

	def daily_sales_report(self):
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {})
		worksheet = workbook.add_worksheet("Daily Sale Report")

		head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px',  'border': 1})
		data_border_format = workbook.add_format({'align': 'left', 'border': 1})
		data_border_format_right = workbook.add_format({'align': 'right', 'border': 1})
		worksheet.merge_range('A1:H1', 'POS Name', head)
		worksheet.write(1,0, 'Date', head)
		format5 = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
		worksheet.write(1,1 , self.date, format5)

		worksheet.write(3,0, 'S no', head,)
		worksheet.write_string(3,1, 'Session no.', head)
		worksheet.write_string(3,2, 'Receipt no.', head)
		worksheet.write(3,3, 'Sale amount', head)
		worksheet.write(3,4, 'GST', head)
		worksheet.write(3,5, 'Net amount', head)
		worksheet.write(3,6, 'Payment mode', head)
		worksheet.write(3,7, 'Sales person', head)

		start_date = datetime.datetime.strptime(str(self.date) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
		end_date = datetime.datetime.strptime(str(self.date) + " 23:59:59", "%Y-%m-%d %H:%M:%S")

		pos_order_ids = self.env['pos.order'].sudo().search([('date_order', '>=', start_date), ('date_order', '<=', end_date)])

		row = 4
		indexing = 1
		for rec in pos_order_ids:
			worksheet.write(row, 0, indexing, data_border_format)
			worksheet.write(row, 1, rec.session_id.name, data_border_format)
			worksheet.write(row, 2, rec.name, data_border_format)
			worksheet.write(row, 3, rec.amount_total, data_border_format)
			worksheet.write(row, 4, rec.lines.tax_ids_after_fiscal_position.name, data_border_format)
			worksheet.write(row, 5, rec.amount_tax, data_border_format)
			worksheet.write(row, 6, rec.payment_ids.payment_method_id.name, data_border_format)
			worksheet.write(row, 7, rec.session_id.user_id.name, data_border_format)
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

		worksheet.merge_range(row+1, 0, row+1, 1, 'Payment summary', head)
		worksheet.write(row+2, 0, 'Cash', data_border_format)
		worksheet.write(row+3, 0, 'Amex', data_border_format)
		worksheet.write(row+4, 0, 'Other Credit card', data_border_format)
		worksheet.write(row+5, 0, 'Alipay/Grabpay/Wechatpay', data_border_format)
		worksheet.write(row+6,0, 'Simplybookme', data_border_format)
		worksheet.write(row+7,0, 'Klook', data_border_format)
		worksheet.write(row+8,0, 'Tipalti', data_border_format)
		worksheet.write(row+9,0, 'Atome', data_border_format)

		cash_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "Cash").mapped("amount"))
		amex_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "AMEX").mapped("amount"))
		credit_card_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "Credit Card").mapped("amount"))
		simplybookme_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "Simplybook Me").mapped("amount"))
		klook_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "Klook").mapped("amount"))
		tipalti_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "Tipalti").mapped("amount"))
		atome_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "ATOME").mapped("amount"))
		alipay_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "ALIPAY").mapped("amount"))
		grabpay_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "GrabPay").mapped("amount"))
		weChat_pay_total = sum(pos_order_ids.payment_ids.filtered(lambda x:x.payment_method_id.name == "WeChat Pay").mapped("amount"))
		alipay_grappay_wechat_pay_total = alipay_total + grabpay_total + weChat_pay_total
		
		worksheet.write(row+2,1, cash_total, data_border_format_right)
		worksheet.write(row+3,1, amex_total, data_border_format_right)
		worksheet.write(row+4,1, credit_card_total, data_border_format_right)
		worksheet.write(row+5,1, alipay_grappay_wechat_pay_total, data_border_format_right)
		worksheet.write(row+6,1, simplybookme_total, data_border_format_right)
		worksheet.write(row+7,1, klook_total, data_border_format_right)
		worksheet.write(row+8,1, tipalti_total, data_border_format_right)
		worksheet.write(row+9,1, atome_total, data_border_format_right)
		workbook.close()
		output.seek(0)
		self.document = b64encode(output.read())
		output.close()

		url = "/web/content/?model=daily.sale.report&field=document&id=%s&filename=%s&download=true"%(self.id, "Daily Sale Report.xlsx")
		return{
			'type' : 'ir.actions.act_url',
			'url': url,
			'target' : 'new',
		}
