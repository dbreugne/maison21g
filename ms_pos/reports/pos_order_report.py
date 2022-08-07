from odoo import models, fields

class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    parent_category_id = fields.Many2one('product.category', string="Parent Product Category", readonly=True)
    
    def _select(self):
        res = super(PosOrderReport, self)._select()
        select_clause = """%s, 
                pc.parent_id as parent_category_id
        """%(res)
        return select_clause
        
    def _from(self):
        res = super(PosOrderReport, self)._from()
        from_clause = """%s
                left join product_category pc on pt.categ_id = pc.id
        """%(res)
        return from_clause

    def _group_by(self):
        res = super(PosOrderReport, self)._group_by()
        group_clause = """%s, 
                pc.parent_id
        """%(res)
        return group_clause