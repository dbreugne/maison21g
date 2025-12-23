from odoo import models, fields,api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    channel_id = fields.Many2one("inom.channel",compute="_compute_partner_classification",store=True,readonly=False)
    category_id = fields.Many2one(
        "inom.category",compute="_compute_category_classification",store=True,readonly=False,
        domain="[('channel_id','=',channel_id)]"
    )
    subcategory_id = fields.Many2one(
        "inom.subcategory",compute="_compute_subcategory_classification",store=True,readonly=False,
        domain="[('category_id','=',category_id)]"
    )
    custom_product_ids = fields.Many2many("product.template",compute="_get_product_category")
    custom_country_ids = fields.Many2many("res.country",compute="_get_country")

    @api.depends("partner_id","partner_id.custom_channel_id")
    def _compute_partner_classification(self):
        for rec in self:
            if rec.partner_id:
                rec.channel_id = rec.partner_id.custom_channel_id
                



    @api.depends("partner_id","partner_id.subcategory_id")
    def _compute_subcategory_classification(self):
        for rec in self:
            if rec.partner_id:
                rec.subcategory_id = rec.partner_id.subcategory_id


    @api.depends("partner_id","partner_id.custom_category_id")
    def _compute_category_classification(self):
        for rec in self:
            if rec.partner_id:
                rec.category_id = rec.partner_id.custom_category_id


    def _get_product_category(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.custom_product_ids:
                rec.custom_product_ids=rec.partner_id.custom_product_ids.ids
            else:
                rec.custom_product_ids=[(6,0,[])]

            

    def _get_country(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.custom_country_ids:
                rec.custom_country_ids=rec.partner_id.custom_country_ids.ids
            else:
                rec.custom_country_ids=[(6,0,[])]

            
