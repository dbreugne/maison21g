from odoo import api, fields, models

class Company(models.Model):

    _inherit = 'res.company'

    location_sub_cont_id = fields.Many2one('stock.location','SubContract Location')