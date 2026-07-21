from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self.filtered(lambda order: order.partner_id in order.message_partner_ids):
            order.message_unsubscribe([order.partner_id.id])
        self._create_invoice_for_api_orders()
        return result

    def _is_invoiceable_without_credit_note(self):
        """An order whose only invoiceable lines sum to a negative amount (e.g. a
        discount) while positive 'invoice on delivery' lines are still undelivered
        must NOT be invoiced yet: Odoo would emit a Customer Credit Note instead of
        an invoice (CN/2026/0016-0038 incident). Deliver first, then invoice."""
        self.ensure_one()
        lines = self.order_line.filtered(lambda l: not l.display_type)
        invoiceable_amount = sum(l.price_unit * l.qty_to_invoice for l in lines)
        if invoiceable_amount >= 0:
            return True
        return not lines.filtered(
            lambda l: l.product_id.invoice_policy == 'delivery'
            and l.price_total > 0
            and l.qty_to_invoice == 0
            and l.qty_invoiced < l.product_uom_qty
        )

    def _create_invoice_for_api_orders(self):
        """Auto-create invoices for orders confirmed via the m21_api integration.

        These orders arrive already paid from external systems (website/booking/
        marketplace), but the integration only confirms them in Odoo without ever
        triggering the invoicing step, so they pile up stuck as 'to invoice'.
        Orders that still need their delivery validated are skipped and must be
        invoiced after delivery.
        """
        api_orders = self.filtered(
            lambda o: o.create_uid.login == 'm21_api'
            and o.invoice_status == 'to invoice'
            and o._is_invoiceable_without_credit_note()
        )
        for order in api_orders:
            order._create_invoices()

    def action_backfill_create_invoices(self):
        """Manually create invoices for selected orders still stuck as 'to invoice'.

        Used to clear the backlog of historical m21_api orders that were
        confirmed (and paid externally) before the auto-invoicing above existed.
        Orders blocked on an unvalidated delivery are skipped (see
        _is_invoiceable_without_credit_note).
        """
        orders = self.filtered(
            lambda o: o.state == 'sale'
            and o.invoice_status == 'to invoice'
            and o._is_invoiceable_without_credit_note()
        )
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
