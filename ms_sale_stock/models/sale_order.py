from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_qty = fields.Float(compute='_compute_available_qty')

    def _compute_available_qty(self):
        sale_warehouse_location_id = self.order_id.warehouse_id.int_type_id.default_location_src_id.id
        domain = [('location_id','=', sale_warehouse_location_id)]
        for line in self:
            domain += [('location_id.usage', '=', 'internal'),
                       ('product_id', 'in', self.product_id.ids),
                    ]
            stock_quant_obj = self.env['stock.quant'].search(domain)
            self.available_qty = stock_quant_obj.quantity