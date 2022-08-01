from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    
    industry_id = fields.Many2one('res.partner.industry', 'Segment', readonly=True)
    parent_category_id = fields.Many2one('product.category', string="Parent Product Category", readonly=True)
    
    def _from(self):
        _from_clause = super(AccountInvoiceReport, self)._from()
        _from_clause += """
            LEFT JOIN product_category categ on template.categ_id = categ.id
        """
        return _from_clause

    @api.model
    def _select(self):
        _select_clause = super(AccountInvoiceReport, self)._select()
        _select_clause += """
            ,categ.parent_id AS parent_category_id,
            partner.industry_id AS industry_id
        """
        return _select_clause
    

    @api.model
    def _group_by(self):
        _group_by = super(AccountInvoiceReport, self)._group_by()
        _group_by += """
            ,categ.parent_id,
            partner.industry_id
        """
        return _group_by