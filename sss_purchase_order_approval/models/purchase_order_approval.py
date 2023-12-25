from odoo import models, fields, api, _, SUPERUSER_ID
import base64
import io
import xlsxwriter


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    user_id = fields.Many2one('res.users', 'User')
    login_user = fields.Boolean(string="Login user", compute='_hide_order_confirm_button', readonly=True)
    state = fields.Selection(selection=[
            ('draft', 'RFQ'),
            ('sent', 'RFQ Sent'),
            ('first_approved', 'First Approvel'),
            ('to approve', 'Second Approvel'),
            ('purchase', 'Purchase Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled')
        ], string='Status')
    # file = fields.Binary()
    # document = fields.Binary('Excel Report')
    # myfile = fields.Char('Excel File', size=64)

    def _auto_send_mail_second_approval_pending(self):
        fp = io.StringIO()
        file_path = "second_approval_pending.xlsx"
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        approve_ids = self.env['purchase.order'].sudo().search([('state', 'in', ['to approve'])])
        partner = self.env['res.users'].sudo().browse(self._context.get('uid'))
        worksheet = workbook.add_worksheet('Purchase order Second Approval Pending Report')
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        head1 = workbook.add_format({'align': 'left', 'bold': False, 'font_size': '10px'})
        worksheet.merge_range('A1:A2', 'Date', head)
        worksheet.merge_range('B1:B2', 'Currency', head)
        worksheet.merge_range('C1:C2', 'SKU', head)
        worksheet.merge_range('D1:D2', 'Description', head)
        worksheet.merge_range('E1:E2', 'SUPPLIER', head)
        worksheet.merge_range('F1:F2', 'ORDER QTY', head)
        worksheet.merge_range('G1:G2', 'Unit Price', head)
        worksheet.merge_range('H1:H2', 'Total Value', head)
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('D:D', 45)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 19)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 25)

        row = 1
        col = 0

        for record in approve_ids:
            worksheet.write(row, col, record.date_order.strftime('%d/%m/%Y %H:%M:%S'), head1)
            worksheet.write(row, col+1, record.currency_id.name, head1)
            worksheet.write(row, col+2, ' ', head1)
            product_total = record.order_line.filtered(lambda x: x.product_id.name).mapped("product_id.name")
            worksheet.write(row, col+3, str(product_total), head1)
            worksheet.write(row, col+4, record.partner_id.name, head1)
            qty_total = sum(record.order_line.filtered(lambda x: x.product_qty).mapped("product_qty"))
            worksheet.write(row, col+5, qty_total, head1)
            unit_price_total = sum(record.order_line.filtered(lambda x: x.price_unit).mapped("price_unit"))
            worksheet.write(row, col+6, unit_price_total, head1)
            worksheet.write(row, col+7, record.amount_total, head1)
            row += 1

        workbook.close()
        datas = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
        file_name = "Second Approval Pending.xlsx"
        attachment_data = {
            'name': file_name,
            'datas': datas,
            'res_model': "modelname",
        }
        attachment_id = self.env['ir.attachment'].sudo().create(attachment_data)
        template_id = self.env.ref('sss_purchase_order_approval.email_send_second_approval_pending')
        template_id.attachment_ids = [(5, 0, [])]
        template_id.attachment_ids = [(4, attachment_id.id)]
        email_to_send_ids = ["Safayat@maison21g.com", "wendy@maison21g.com"]
        # cc_emails = ["Safayat@maison21g.com", "wendy@maison21g.com"]
        cc_emails = False
        for email_to in email_to_send_ids:
            users_name = self.env['res.users'].search([('login', '=', email_to)])
            email_values = {
                'email_to': email_to,
                'email_cc': cc_emails,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
            }
            template_id.with_context(user_name=users_name.name, partner_from_name=partner.name, partner_from_email=partner.email).send_mail(self.id, force_send=True, email_values=email_values)

    def _all_status_po(self):
        fp = io.StringIO()
        file_path = "po_all_status_report.xlsx"
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        # purchase_id = self.env['purchase.order'].sudo().search([('state', 'not in', ['purchase', 'done'])])
        purchase_id = self.env['purchase.order'].sudo().search([])
        partner = self.env['res.users'].sudo().browse(self._context.get('uid'))
        worksheet = workbook.add_worksheet('Purchase order Second Approval Pending Report')
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        head1 = workbook.add_format({'align': 'left', 'bold': False, 'font_size': '10px'})
        worksheet.write(0, 0, 'Date', head)
        worksheet.write(0, 1, 'PO#', head)
        worksheet.write(0, 2, 'Approved On', head)
        worksheet.write(0, 3, 'Currency', head)
        worksheet.write(0, 4, 'SKU', head)
        worksheet.write(0, 5, 'Product Name', head)
        worksheet.write(0, 6, 'SUPPLIER', head)
        worksheet.write(0, 7, 'ORDER QTY', head)
        worksheet.write(0, 8, 'Unit Price', head)
        worksheet.write(0, 9, 'Total value', head)
        worksheet.write(0, 10, 'PO Approval Status', head)
        worksheet.set_column(0, 1, 25)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(5, 5, 40)
        worksheet.set_column(6, 6, 35)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 25)
        worksheet.set_column(9, 9, 25)
        worksheet.set_column(10, 10, 30)
        row = 2

        col = 0
        for record in purchase_id:
            for line in record.order_line:
                worksheet.write(row, col+0, record.date_order.strftime('%d/%m/%Y %H:%M:%S'), head1)
                worksheet.write(row, col+1, record.name, head1)
                worksheet.write(row, col+2, record.date_approve.strftime('%d/%m/%Y %H:%M:%S') if record.date_approve else record.date_approve, head1)
                worksheet.write(row, col+3, record.currency_id.name, head1)
                worksheet.write(row, col+4, 'SKU', head1)
                worksheet.write(row, col+5, line.product_id.display_name, head1)
                worksheet.write(row, col+6, record.partner_id.name, head1)
                worksheet.write(row, col+7, line.product_qty, head1)
                worksheet.write(row, col+8, line.price_unit, head1)
                worksheet.write(row, col+9, record.amount_total, head1)
                worksheet.write(row, col+10, record.state, head1)
                row += 1
        workbook.close()
        datas = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
        file_name = "Purchase Order.xlsx"
        attachment_data = {
            'name': file_name,
            'datas': datas,
            'res_model': "modelname",
        }
        attachment_id = self.env['ir.attachment'].sudo().create(attachment_data)
        template_id = self.env.ref('sss_purchase_order_approval.email_send_all_status_po')
        template_id.attachment_ids = [(5, 0, [])]
        template_id.attachment_ids = [(4, attachment_id.id)]
        email_to_send_ids = ["wendy@maison21g.com", "Safayat@maison21g.com", "rick@maison21g.com", "xintong@maison21g.com", "camille@maison21g.com", "johanna@maison21g.com", "ayaba@maison21g.com", "accounting@maison21g.com"]
        # email_to_send_ids = ["aneri.spellbound@gmail.com"]
        cc_emails = ["Safayat@maison21g.com", "wendy@maison21g.com"]
        cc_emails = False
        for email_to in email_to_send_ids:
            users_name = self.env['res.users'].search([('login', '=', email_to)])
            email_values = {
                'email_to': email_to,
                'email_cc': cc_emails,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
            }
            template_id.with_context(user_name=users_name.name, partner_from_name=partner.name, partner_from_email=partner.email).send_mail(self.id, force_send=True, email_values=email_values)

    @api.model
    def create(self, values):
        res = super(PurchaseOrder, self).create(values)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('purchase.purchase_rfq')
        menu_id = self.env.ref('purchase.menu_purchase_root')
        base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s" % (res.id, action_id.id, res.company_id.id, menu_id.id)
        partner = self.env['res.users'].browse(self._context.get('uid'))
        template_id = self.env.ref('sss_purchase_order_approval.email_send_first_approval')
        to_send_email_ids = ["wendy@maison21g.com", "rick@maison21g.com"]
        # to_send_email_ids = ["aneri.spellbound@gmail.com"]
        for to_mail in to_send_email_ids:
            users_name = self.env['res.users'].search([('login', '=', to_mail)])
            email_values = {
                'email_to': to_mail,
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
            }
            template_id.with_context(partner_from_name=partner.name, partner_from_email=partner.email, my_url=base_url, user_name=users_name.name).send_mail(res.id, force_send=True, email_values=email_values)

        return res

    @api.depends('user_id')
    def _hide_order_confirm_button(self):
        for rec in self:
            if self.env.user.name in ['Wendy', 'Rick'] or rec.user_has_groups('purchase.group_purchase_manager'):
                rec.login_user = True
            else:
                rec.login_user = False

    def button_first_approve(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('purchase.purchase_rfq')
        menu_id = self.env.ref('purchase.menu_purchase_root')
        base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s" % (self.id, action_id.id, self.company_id.id, menu_id.id)
        partner = self.env['res.users'].browse(self._context.get('uid'))
        template_id = self.env.ref('sss_purchase_order_approval.email_send_second_approval')
        to_send_email_ids = ["camille@maison21g.com", "johanna@maison21g.com"]
        # to_send_email_ids = ["aneri.spellbound@gmail.com", "maxime@maison21g.com"]
        for to_mail in to_send_email_ids:
            users_name = self.env['res.users'].search([('login', '=', to_mail)])
            email_values = {
                'email_to': to_mail,
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
            }
            template_id.with_context(partner_from_name=partner.name, partner_from_email=partner.email, my_url=base_url, user_name=users_name.name).send_mail(self.id, force_send=True, email_values=email_values)
        self.state = 'to approve'

    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve(force=force)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('purchase.purchase_rfq')
        menu_id = self.env.ref('purchase.menu_purchase_root')
        base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s" % (self.id, action_id.id, self.company_id.id, menu_id.id)
        partner = self.env['res.users'].browse(self._context.get('uid'))
        template_id = self.env.ref('sss_purchase_order_approval.email_send_approved')
        to_send_email_ids = ["safayat@maison21g.com", "wendy@maison21g.com", "accounting@maison21g.com", "ayaba@maison21g.com"]
        # to_send_email_ids = ["aneri.spellbound@gmail.com"]
        for to_mail in to_send_email_ids:
            users_name = self.env['res.users'].search([('login', '=', to_mail)])
            email_values = {
                'email_to': to_mail,
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
            }
            template_id.with_context(partner_from_name=partner.name, partner_from_email=partner.email, my_url=base_url, user_name=users_name.name).send_mail(self.id, force_send=True, email_values=email_values)
        self.button_unlock()
        return res
