
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MultiDo(models.TransientModel):
    """Create a new wizard multi.do.wiz"""
    _name = 'multi.do.wiz'
    _description = 'Multi DO Wizard'

    # pick_ids = fields.Many2many('stock.picking', 'stock_picking_transfer_rel')


    def confirm_multi_do(self):
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids'))
        for picking in picking_ids:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(_(
                            "Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        if pick_to_do:
            pick_to_do.action_done()
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False
