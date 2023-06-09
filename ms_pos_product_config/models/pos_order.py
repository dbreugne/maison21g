from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    bottle_line_id = fields.Many2one("pos.order.line", compute='_get_bottle_line', store=True)
    bottle_line_idx = fields.Char()
    bottle_product_id = fields.Many2one("product.product", related="bottle_line_id.product_id", store=True, string="Bottle Product")
    is_bottle = fields.Boolean(related="product_id.is_bottle" , store=True)
    is_scent = fields.Boolean(related="product_id.is_scent" , store=True)

    @api.depends('bottle_line_idx')
    def _get_bottle_line(self):
        if not self._context.get('module', False):
            for line in self:
                bottle_line = False
                if line.bottle_line_idx:
                    idx = int(line.bottle_line_idx)
                    bottle_line = line.order_id.lines[idx]
                if bottle_line:
                    line.bottle_line_id = bottle_line.id
