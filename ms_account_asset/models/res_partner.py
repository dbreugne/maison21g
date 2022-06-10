from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    industry_id = fields.Many2one('res.partner.industry', 'Segment')

    