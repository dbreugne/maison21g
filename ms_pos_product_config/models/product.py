from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_scent = fields.Boolean('Scent', help="Indicates that this product is a scent")
    is_bottle = fields.Boolean('Bottle', help="Indicates that this product is a bottle")
    max_number_of_scents = fields.Integer(help="maximum number of scents")

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    is_scent = fields.Boolean('Scent', related="product_tmpl_id.is_scent", readonly=False)
    is_bottle = fields.Boolean('Bottle', related="product_tmpl_id.is_bottle", readonly=False)
    max_number_of_scents = fields.Integer(related="product_tmpl_id.max_number_of_scents", readonly=False)