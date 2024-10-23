# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

from odoo import models, fields, api, _

class dev_pos_config(models.Model):
    _inherit = 'pos.config'
    
    load_pos_order = fields.Boolean(string='POS Orders', default=True)
    last_days = fields.Char("Last Days",default=120)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    load_pos_order = fields.Boolean(related="pos_config_id.load_pos_order",readonly=False,)
    last_days = fields.Char(related="pos_config_id.last_days", readonly=False)


class posOrder(models.Model):
    _inherit = 'pos.order'

    def pos_order_reprint_data(self):
        orderlines = []
        paymentlines = []
        discount = 0

        for ol in self.lines:
            order_data = {
                'id': ol.id,
                'product_id': ol.product_id.name,
                'qty': ol.qty,
                'price_unit': ol.price_unit,
                'discount': ol.discount,
                'total_price' : ol.price_subtotal_incl,
                }
                
            discount += (ol.price_unit * ol.qty * ol.discount) / 100
            orderlines.append(order_data)

        for pay in self.payment_ids:
            if pay.amount > 0:
                temp = {
                    'id':pay.id,
                    'amount': pay.amount,
                    'name': pay.payment_method_id.name
                }
                paymentlines.append(temp)

        reprintData = {
            'discount': discount,
            'orderlines': orderlines,
            'paymentlines': paymentlines,
            'change': self.amount_return,
            'subtotal': self.amount_total - self.amount_tax,
            'tax': self.amount_tax,
            'user_name' : self.user_id.name
        }

        return reprintData

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
