from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        for order in self:
            invoiceable_amount = sum(
                line.price_unit * line.qty_to_invoice
                for line in order.order_line
                if not line.display_type
            )
            undelivered_lines = order.order_line.filtered(
                lambda l: not l.display_type
                and l.product_id.invoice_policy == 'delivery'
                and l.price_total > 0
                and l.qty_to_invoice == 0
                and l.qty_invoiced < l.product_uom_qty
            )
            if invoiceable_amount < 0 and undelivered_lines:
                raise UserError(_(
                    'Cannot invoice %(order)s: the products %(products)s are '
                    'invoiced on delivery and have not been delivered yet, so '
                    'only negative lines (discounts) would be invoiced and Odoo '
                    'would create a Customer Credit Note instead of an invoice. '
                    'Validate the delivery first, then invoice the full order.',
                    order=order.name,
                    products=', '.join(undelivered_lines.mapped('product_id.display_name')),
                ))
        return super()._create_invoices(grouped=grouped, final=final, date=date)
