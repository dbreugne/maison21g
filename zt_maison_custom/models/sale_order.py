from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit='sale.order'

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self.filtered(lambda order: order.partner_id in order.message_partner_ids):
            order.message_unsubscribe([order.partner_id.id])
        return result