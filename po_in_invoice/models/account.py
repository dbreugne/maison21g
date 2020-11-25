from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # po_no = fields.Char("PO No")
