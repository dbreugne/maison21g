from odoo import api, fields, models, _
from operator import itemgetter

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    available_qty = fields.Float(compute='_compute_available_qty')
    
    
    @api.depends('quantity')
    def _compute_available_qty(self):
        for quant in self:
            allowed_move_status = ['draft', 'waiting', 'confirmed', 'assigned']
            
            related_moves = self.env['stock.move'].search([
                ('product_id', '=', quant.product_id.id),
                ('state', 'in', allowed_move_status),
                ('location_id', '=', quant.location_id.id),
            ])
            outgoing_qty = 0
            different_uom = related_moves.filtered(lambda mv: mv.product_uom.id != False and mv.product_uom.id != quant.product_uom_id.id)
            if len(different_uom):
                for move in different_uom:
                    outgoing_qty += move.product_uom._compute_quantity(move.product_uom_qty, quant.product_uom_id)

            same_uom = related_moves - different_uom
            outgoing_qty += sum(same_uom.mapped('product_uom_qty'))
            quant.sudo()._compute_inventory_quantity()
            quant.available_qty = quant.quantity - outgoing_qty