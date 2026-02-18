from odoo import models, fields, api
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    brand_id = fields.Many2one('customer.brand', string="Brand Name")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        if name:
            domain = expression.OR([
                [('name', operator, name)],
                [('brand_id.name', operator, name)],
            ])
            args = expression.AND([args, domain])

        return super().name_search(name='', args=args, operator=operator, limit=limit)
