from odoo import models, fields,api


class pack_product(models.Model):
    _name = 'pack.product'

    product_new_name  = fields.Many2one('product.template',string="Product")
    product_new_name_trial = fields.Many2one('product.product', string="Product")
    qty_new = fields.Float("Quantity")
