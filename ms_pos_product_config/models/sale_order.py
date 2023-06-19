from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bottle_ids = fields.Many2many(
        'product.product', compute='_get_bottle_list')

    @api.depends('order_line.product_id')
    def _get_bottle_list(self):
        if not self._context.get('module', False):
            for order in self:
                bottle_product_ids = order.order_line.filtered(
                    lambda l: l.product_id.id != False and l.product_id.is_bottle
                ).mapped('product_id')
                order.bottle_ids = [(6, 0, bottle_product_ids.ids)]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bottle_id = fields.Many2one('product.product')
    is_scent = fields.Boolean(related='product_id.is_scent')

    @api.onchange('product_id')
    def onchange_bottle_id(self):
        for line in self:
            if line.product_id and line.product_id.is_scent:
                bottle_obj = line.order_id.bottle_ids
                if bottle_obj:
                    domain = [('id', 'in', bottle_obj.ids)]
                    return {'domain': {'bottle_id': domain}}
            return {'domain': {'bottle_id': [('id', 'in', [])]}}
