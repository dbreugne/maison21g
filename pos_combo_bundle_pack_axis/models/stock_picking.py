from odoo import models


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        res = super(stock_picking,self).write(vals)
        list = []
        for move_line in self.move_line_ids_without_package:
            for product in move_line.product_id:
                if product.pack_product_ids:
                    self.move_ids_without_package.write({'state':'draft'})
                    move_line.unlink()
        for move_line in self.move_ids_without_package:
            for product in move_line.product_id:
                if product.pack_product_ids:
                    for pack_products_id in product.pack_product_ids:
                        if len(product.pack_product_ids.ids) == 1:
                            move_line.write({'product_id':pack_products_id.product_new_name_trial.id,
                                             'product_uom_qty': pack_products_id.qty_new*move_line.product_uom_qty})
                        elif len(product.pack_product_ids.ids) > 1:
                            if move_line not in list:
                                list.append(move_line)
                            self.env['stock.move'].create({'name':'test',
                              'picking_id': self.id,
                              'product_id':pack_products_id.product_new_name_trial.id,
                              'product_uom':pack_products_id.product_new_name_trial.uom_id.id,
                              'location_id': move_line.location_id.id,
                              'location_dest_id': move_line.location_dest_id.id,
                              'product_uom_qty':pack_products_id.qty_new*move_line.product_uom_qty})
        for move in list:
            move.unlink()
        # self.action_confirm()
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        
        if moves:        
            self.action_assign()            
            self.button_validate()
            self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]}).process()
        
        return res