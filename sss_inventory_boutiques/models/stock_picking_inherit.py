from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPickingInerit(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('approve', 'Approve'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('reject', 'Reject'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    def approve_button(self):
        self.state = 'approve'

    def reject_button(self):
        self.state = 'reject'

    # @api.depends('state', 'is_locked')
    # def _compute_show_validate(self):
    #     res = super(StockPickingInerit, self)._compute_show_validate()
    #     for picking in self:
    #         if picking.picking_type_code == 'internal':
    #             if not (picking.immediate_transfer) and picking.state == 'draft':
    #                 picking.show_validate = False
    #             elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned', 'approve', 'reject') or not picking.is_locked:
    #                 picking.show_validate = False
    #             else:
    #                 picking.show_validate = True
    #         else:
    #             return res

    # def _compute_show_check_availability(self):
    #     """ According to `picking.show_check_availability`, the "check availability" button will be
    #     displayed in the form view of a picking.
    #     """
    #     res = super(StockPickingInerit, self)._compute_show_check_availability()
    #     for picking in self:
    #         if picking.picking_type_code == 'internal':
    #             if picking.immediate_transfer or not picking.is_locked or picking.state not in ('confirmed', 'waiting', 'assigned', 'approve'):
    #                 picking.show_check_availability = False
    #                 continue
    #             picking.show_check_availability = any(
    #                 move.state in ('waiting', 'confirmed', 'partially_available', 'approve') and
    #                 float_compare(move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding)
    #                 for move in picking.move_lines
    #             )
    #         else:
    #             return res
