from odoo import models, fields,api

class ResPartner(models.Model):
    _inherit = "res.partner"



    custom_channel_id = fields.Many2one("inom.channel")
    custom_category_id = fields.Many2one("inom.category")
    subcategory_id = fields.Many2one("inom.subcategory")
    available_product_ids = fields.Many2many('product.template',compute="_compute_product_ids",store=True)
    available_country_ids = fields.Many2many('res.country',compute="_compute_country_ids",store=True)
    
    product_ids = fields.Many2many("product.template","res_partner_rel")
    country_ids = fields.Many2many("res.country","res_partner_country_rel")


    @api.depends('custom_category_id','subcategory_id')
    def _compute_country_ids(self):
        for rec in self:
            if rec.subcategory_id:
                rec.available_country_ids=[(6,0,rec.subcategory_id.country_ids.ids)]
                
                #print("4444444444444444444",rec.subcategory_id.product_ids)
            elif rec.custom_category_id:
                #print("4444444444444444444",rec.custom_category_id.product_ids)
                rec.available_country_ids=[(6,0,rec.custom_category_id.country_ids.ids)]
            else:
                rec.available_country_ids=[(6,0,[])]

                


    @api.depends('custom_category_id','subcategory_id')
    def _compute_product_ids(self):
        for rec in self:
            if rec.subcategory_id:
                rec.available_product_ids=[(6,0,rec.subcategory_id.product_ids.ids)]
                
                #print("4444444444444444444",rec.subcategory_id.product_ids)
            elif rec.custom_category_id:
                #print("4444444444444444444",rec.custom_category_id.product_ids)
                rec.available_product_ids=[(6,0,rec.custom_category_id.product_ids.ids)]
                #rec.available_country_ids=rec.custom_category_id.country_ids.ids
            else:
                rec.available_product_ids=[(6,0,[])]


    
