from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = "account.move"

    po_number = fields.Char('PO No')

#Attachment Access Issue for General Users.

class Attachment(models.Model):

    _inherit = ['ir.attachment']

    @api.model
    def check(self, mode, values=None):
        if self.env.user.has_group('point_of_sale.group_pos_user'):
            super(Attachment, self).sudo().check(mode, values)
        super(Attachment, self).check(mode, values)