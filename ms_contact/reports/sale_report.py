from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    industry_id = fields.Many2one('res.partner.industry', 'Segment', readonly=True)
    parent_category_id = fields.Many2one('product.category', string="Parent Product Category", readonly=True)

    # def _query(self):
    #     fields.update({'parent_category_id': ', pc.parent_id as parent_category_id'})
    #     from_clause += 'left join product_category pc on t.categ_id = pc.id'
    #     groupby += ', pc.parent_id'
    #     return super(SaleReport, self)._query()
