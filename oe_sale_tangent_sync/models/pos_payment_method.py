from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    tangent_payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('nets', 'Nets'),
        ('visa', 'Credit Card'),
        ('master', 'Not Used'),
        ('amex', 'Amex'),
        ('voucher', 'Voucher'),
        ('others', 'Other payment method group up together'),
        ('no_sync', 'Not Synced')
    ], string='Tangent payment method', default='no_sync', help='Payment method that will be used to group orders and sent to Tangent Apps')
