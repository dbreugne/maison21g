from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ReportPosOrder(models.Model):
    _inherit = 'report.pos.order'

    bottle_product_id = fields.Many2one("product.product")
    is_bottle = fields.Boolean()
    is_scent = fields.Boolean()

    def _select(self):
        res = super(ReportPosOrder, self)._select()
        res += """
        ,l.bottle_product_id
        ,l.is_bottle
        ,l.is_scent
        """
        return res

    def _group_by(self):
        res = super(ReportPosOrder, self)._group_by()
        res += """
        ,l.bottle_product_id
        ,l.is_bottle
        ,l.is_scent
        """
        return res    