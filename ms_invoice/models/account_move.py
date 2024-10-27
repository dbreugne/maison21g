from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    subtotal_non_tax = fields.Monetary(string='Subtotal Without Tax', store=True, readonly=True,
                                       currency_field='currency_id', compute='_compute_subtotal_non_tax')

    @api.depends('price_unit', 'quantity')
    def _compute_subtotal_non_tax(self):
        for line in self:
            subtotal_non_tax = line.price_unit * line.quantity
            line.subtotal_non_tax = subtotal_non_tax
