# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api

class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"


    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLineInherit, self).onchange_product_id()
        for rec in self:
            if rec.product_id and not rec.order_id.partner_id.country_id.name == 'Singapore':
                rec.taxes_id = False
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total', 'partner_id')
    def _amount_all(self):
        res = super(PurchaseOrder, self)._amount_all()
        if self.amount_total > 1000 and self.partner_id.country_id.name == 'China':
            payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_30%deposite70%payment')
            # payment_term_id = self.env['account.payment.term'].search([('name', 'ilike', '30% deposit 70% payment')])
            self.payment_term_id = payment_term_id.id
        else:
            payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_100%payment')
            # payment_term_id = self.env['account.payment.term'].search([('name', 'ilike', '100% payment')])
            self.payment_term_id = payment_term_id.id
        return res

    @api.onchange('partner_id')
    def _onchnage_partner_id(self):
        for rec in self.order_line:
            if rec.product_id and not rec.order_id.partner_id.country_id.name == 'Singapore':
                rec.taxes_id = False
        return res


    def button_approve(self, force= False):
        res = super(PurchaseOrder, self).button_approve(force=force)
        if self.amount_total > 1000 and self.partner_id.country_id.name == 'China':
            payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_30%deposite70%payment')
            self.payment_term_id = payment_term_id.id
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action_id = self.env.ref('purchase.purchase_rfq')
            menu_id = self.env.ref('purchase.menu_purchase_root')
            base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s"%(self.id, action_id.id, self.company_id.id, menu_id.id)
            partner = self.env['res.users'].browse(self._context.get('uid'))
            template_id = self.env.ref('sss_vendor_payment_term.email_send_account_payment_term')
            to_send_email_ids = ["accounting@maison21g.com"]
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
        else:
            payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_100%payment')
            self.payment_term_id = payment_term_id.id
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action_id = self.env.ref('purchase.purchase_rfq')
            menu_id = self.env.ref('purchase.menu_purchase_root')
            base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s"%(self.id, action_id.id, self.company_id.id, menu_id.id)
            partner = self.env['res.users'].browse(self._context.get('uid'))
            template_id = self.env.ref('sss_vendor_payment_term.email_send_account_100%payment_term')
            to_send_email_ids = ["accounting@maison21g.com"]
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
        return res



# class PurchaseAdvancePaymentInv(models.TransientModel):
#     _inherit = "purchase.advance.payment.inv"


#     def _create_invoice(self, order, po_line, amount):
#         res = super(PurchaseAdvancePaymentInv, self)._create_invoice(order, po_line, amount)
#         Purchase = self.env["purchase.order"]
#         purchases = Purchase.browse(self._context.get("active_ids", []))
#         if self.amount == 30 and purchases.amount_total > 1000 and purchases.partner_id.country_id.name == 'China':
#             payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_30%deposite')
#             res.invoice_payment_term_id = payment_term_id.id
#         elif self.amount == 70 and purchases.amount_total > 1000 and purchases.partner_id.country_id.name == 'China':
#             payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_70%payment')
#             res.invoice_payment_term_id = payment_term_id.id
#             print("::::DFSFD:::::::::::::::;",payment_term_id.name)
#             # a
#         return res

    # def create_invoices(self):
    #     res = super(PurchaseAdvancePaymentInv, self).create_invoices()
    #     Purchase = self.env["purchase.order"]
    #     purchases = Purchase.browse(self._context.get("active_ids", []))
        # if purchases.amount_total > 1000 and purchases.partner_id.country_id.name == 'China':
        #     payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_70%payment')
        #     purchases.payment_term_id = payment_term_id.id
        #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #     action_id = self.env.ref('purchase.purchase_rfq')
        #     menu_id = self.env.ref('purchase.menu_purchase_root')
        #     base_url += "/web#id=%s&action=%s&model=purchase.order&view_type=form&cids=%s&menu_id=%s"%(purchases.id, action_id.id, purchases.company_id.id, menu_id.id)
        #     partner = self.env['res.users'].browse(self._context.get('uid'))
        #     template_id = self.env.ref('sss_vendor_payment_term.email_send_account_70%payment_term')
        #     to_send_email_ids = ["accounting@maison21g.com"]
        #     for to_mail in to_send_email_ids:
        #         users_name = self.env['res.users'].search([('login', '=', to_mail)])
        #         email_values = {
        #             'email_to': to_mail,
        #             'email_cc': False,
        #             'auto_delete': True,
        #             'recipient_ids': [],
        #             'partner_ids': [],
        #             'scheduled_date': False,
        #         }
        #         template_id.with_context(partner_from_name=partner.name, partner_from_email=partner.email, my_url=base_url, user_name=users_name.name).send_mail(purchases.id, force_send=True, email_values=email_values)
        # else:
        #     payment_term_id = self.env.ref('sss_vendor_payment_term.account_payment_term_100%payment')
        # return res
