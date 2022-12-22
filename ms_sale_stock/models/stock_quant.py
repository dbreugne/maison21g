from odoo import api, fields, models, _
from operator import itemgetter

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    available_qty = fields.Float(compute='_compute_available_qty')
    
    def _compute_available_qty(self):
        for quant in self:
            allowed_move_status = ['draft', 'waiting', 'confirmed', 'assigned', 'done']
            
            related_moves = self.env['stock.move'].search([
                ('product_id', '=', quant.product_id.id),
                ('state', 'in', allowed_move_status),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'customer'),
            ])
            outgoing_qty = 0
            different_uom = related_moves.filtered(lambda mv: mv.product_uom.id != False and mv.product_uom.id != quant.product_uom_id.id)
            if len(different_uom):
                for move in different_uom:
                    outgoing_qty += move.product_uom._compute_quantity(move.product_uom_qty, quant.product_uom_id)

            same_uom = related_moves - different_uom
            outgoing_qty += sum(same_uom.mapped('product_uom_qty'))
            quant.available_qty = quant.inventory_quantity - outgoing_qty