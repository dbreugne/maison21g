from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    industry_id = fields.Many2one('res.partner.industry', 'Segment', required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get('industry_id', 0):
            res.update({'industry_id': ''})
        return res
