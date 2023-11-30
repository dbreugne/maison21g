# -*- coding: utf-8 -*-
# Part of Linserv. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _, SUPERUSER_ID
import base64
import io
import xlsxwriter
from base64 import b64encode


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    file = fields.Binary()
    document = fields.Binary('Excel Report')
    myfile = fields.Char('Excel File', size=64)

    def _cron_generate_mail(self):
        fp = io.StringIO()
        file_path = "Purchase.xlsx"
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        res = self.env['purchase.order'].search(
            [('state', 'in', ['draft', 'sent', 'to approve'])])
        worksheet = workbook.add_worksheet('Purchase Report')
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px'})
        worksheet.merge_range('A1:A2', 'Order Date', head)
        worksheet.merge_range('B1:B2', 'Purchase Order No', head)
        worksheet.merge_range('C1:C2', 'Vendor', head)
        worksheet.merge_range('D1:D2', 'Product', head)
        worksheet.merge_range('E1:E2', 'Description', head)
        worksheet.merge_range('F1:F2', 'Quantity', head)
        worksheet.merge_range('G1:G2', 'UOM', head)
        worksheet.merge_range('H1:H2', 'Unit Price', head)
        worksheet.merge_range('I1:I2', 'Currency', head)
        worksheet.merge_range('J1:J2', 'Supplier ETD', head)
        worksheet.merge_range('K1:K2', 'Tracking info', head)
        worksheet.merge_range('L1:L2', 'ETA', head)
        worksheet.merge_range('M1:M2', 'Purchase Order Link', head)

        row = 3
        for obj in res:
            partner = self.env['res.users'].browse(self._context.get('uid'))
            for rec in obj.order_line:
                base_url = self.env['ir.config_parameter'].sudo(
                ).get_param('web.base.url')
                action_id = self.env.ref('purchase.purchase_rfq')
                menu_id = self.env.ref('purchase.menu_purchase_root')
                base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s" % (
                    obj.id, action_id.id, obj.company_id.id, menu_id.id)
                worksheet.write(
                    row, 0, obj.date_order.strftime('%d/%m/%Y %H:%M:%S'))
                worksheet.write(row, 1, obj.name)
                worksheet.write(row, 2, obj.partner_id.name)
                worksheet.write(row, 3, rec.product_id.display_name)
                worksheet.write(row, 4, obj.name)
                worksheet.write(row, 5, rec.product_qty)
                worksheet.write(row, 6, rec.product_uom.name)
                worksheet.write(row, 7, ('{:,.3f}'.format(rec.price_unit)))
                worksheet.write(row, 8, obj.currency_id.name)
                worksheet.write(row, 9, obj.x_studio_supplier_etd.strftime(
                    '%d/%m/%Y') if obj.x_studio_supplier_etd else '')
                worksheet.write(row, 10, obj.x_studio_tracking_info)
                worksheet.write(row, 11, obj.x_studio_eta.strftime(
                    '%d/%m/%Y') if obj.x_studio_eta else '')
                worksheet.write(row, 12, base_url)
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 18)
                worksheet.set_column('C:C', 30)
                worksheet.set_column('D:D', 30)
                worksheet.set_column('E:E', 18)
                worksheet.set_column('F:F', 10)
                worksheet.set_column('G:G', 10)
                worksheet.set_column('H:H', 10)
                worksheet.set_column('I:I', 10)
                worksheet.set_column('J:J', 10)
                worksheet.set_column('K:K', 30)
                worksheet.set_column('L:L', 10)
                worksheet.set_column('M:M', 100)
                row += 1

        workbook.close()
        datas = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
        file_name = "Undelivered Purchase Order.xlsx"
        attachment_data = {
            'name': file_name,
            'datas': datas,
        }
        attachment_id = self.env['ir.attachment'].sudo().create(
            attachment_data)
        template_id = self.env.ref(
            'sss_shipment_tracking_for_incoming_purchase_orders.email_send_confirm')
        template_id.attachment_ids = [(5, 0, [])]
        template_id.attachment_ids = [(4, attachment_id.id)]

        email_to_send_ids = ["wendy@maison21g.com", "xintong@maison21g.com", "rick@maison21g.com",
                             "jonathan@maison21g.com", " muhamand@maison21g.com", "muhammad@maison21g.com", "manisha@maison21g.com", "aneri.spellbound@gmail.com"]
        # email_to_send_ids = ["wendy@maison21g.com", "aneri.spellbound@gmail.com"]
        for email_to in email_to_send_ids:
            email_values = {
                'email_to': email_to,
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
            }
            template_id.with_context(partner_from=partner.email).send_mail(
                obj.id, force_send=True, email_values=email_values)
