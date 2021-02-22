from odoo import models, fields, api


class Product(models.Model):

    _inherit = "product.template"

    is_pos_master = fields.Boolean('Master Product Category')
