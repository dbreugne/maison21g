from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_qty = fields.Float(compute='_compute_available_qty')

    def _compute_available_qty(self):
        sale_warehouse_location_id = self.order_id.warehouse_id.lot_stock_id.id
        warehouse_internal_locations = self.env['stock.location'].search([
            ('location_id', '=', sale_warehouse_location_id),
            ('usage', '=', 'internal'),
        ])
        for line in self:
            domain = [
                ('location_id', 'in', warehouse_internal_locations.ids),
                ('product_id', 'in', line.product_id.ids),
            ]
            stock_quant_obj = self.env['stock.quant'].search(domain)
            stock_quant_obj._compute_available_qty()
            line.available_qty = sum(stock_quant_obj.mapped('available_qty'))