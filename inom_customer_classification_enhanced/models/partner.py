from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"



    custom_channel_id = fields.Many2one("inom.channel")
    custom_category_id = fields.Many2one("inom.category")
    subcategory_id = fields.Many2one("inom.subcategory")
