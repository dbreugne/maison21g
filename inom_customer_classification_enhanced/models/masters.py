from odoo import models, fields

class InomChannel(models.Model):
    _name = "inom.channel"
    _description = "Channel"
    name = fields.Char(required=True)

class InomCategory(models.Model):
    _name = "inom.category"
    _description = "Category"
    name = fields.Char(required=True)
    channel_id = fields.Many2one("inom.channel", required=True)
    product_ids = fields.Many2many("product.template")
    country_ids = fields.Many2many("res.country")

class InomSubCategory(models.Model):
    _name = "inom.subcategory"
    _description = "Sub Category"
    name = fields.Char(required=True)
    category_id = fields.Many2one("inom.category", required=True)
    product_ids = fields.Many2many("product.template")
    country_ids = fields.Many2many("res.country")

class InomHQCategory(models.Model):
    _name = "inom.hq.category"
    _description = "HQ Category"
    name = fields.Char(required=True)
