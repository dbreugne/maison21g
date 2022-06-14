from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleReport(models.Model):
    _inherit = 'sale.report'
    
    industry_id = fields.Many2one('res.partner.industry', 'Segment', readonly=True)

    