from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = "account.move"

    po_number = fields.Char('PO No')