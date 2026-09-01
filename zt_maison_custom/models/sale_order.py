from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self.filtered(lambda order: order.partner_id in order.message_partner_ids):
            order.message_unsubscribe([order.partner_id.id])
        self._create_invoice_for_api_orders()
        return result

    def _create_invoice_for_api_orders(self):
        """Auto-create invoices for orders confirmed via the m21_api integration.

        These orders arrive already paid from external systems (website/booking/
        marketplace), but the integration only confirms them in Odoo without ever
        triggering the invoicing step, so they pile up stuck as 'to invoice'.
        """
        api_orders = self.filtered(
            lambda o: o.create_uid.login == 'm21_api' and o.invoice_status == 'to invoice'
        )
        for order in api_orders:
            order._create_invoices()

    def action_backfill_create_invoices(self):
        """Manually create invoices for selected orders still stuck as 'to invoice'.

        Used to clear the backlog of historical m21_api orders that were
        confirmed (and paid externally) before the auto-invoicing above existed.
        """
        orders = self.filtered(lambda o: o.state == 'sale' and o.invoice_status == 'to invoice')
        invoices = self.env['account.move']
        for order in orders:
            invoices |= order._create_invoices()
        if not invoices:
            return
        return {
            'name': _('Created Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
        }
