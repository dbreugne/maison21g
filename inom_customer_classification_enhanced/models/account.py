from odoo import models, fields,api

class AccountMove(models.Model):
    _inherit = "account.move"
    channel_id = fields.Many2one("inom.channel",compute="_compute_partner_classification",store=True,readonly=False)
    category_id = fields.Many2one(
        "inom.category",compute="_compute_category_classification",store=True,readonly=False,
        domain="[('channel_id','=',channel_id)]"
    )
    subcategory_id = fields.Many2one(
        "inom.subcategory",compute="_compute_subcategory_classification",store=True,readonly=False,
        domain="[('category_id','=',category_id)]"
    )

    custom_product_ids = fields.Many2many("product.template",compute="_get_product_category",string="products")
    custom_country_ids = fields.Many2many("res.country",compute="_get_country",string="Country")

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
                rec.custom_product_ids=[(6,0,rec.partner_id.custom_product_ids.ids)]
            else:
                rec.custom_product_ids=[(6,0,[])]


    def _get_country(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.custom_country_ids:
                rec.custom_country_ids=[(6,0,rec.partner_id.custom_country_ids.ids)]
            else:
                rec.custom_country_ids=[(6,0,[])]
    # @api.onchange("partner_id")
    # def _onchange_partner_classification(self):
    #     if self.partner_id:
    #         self.channel_id = self.partner_id.custom_channel_id
    #         self.category_id = self.partner_id.custom_category_id
    #         self.subcategory_id = self.partner_id.subcategory_id

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    custom_sale_id = fields.Many2one('sale.order',string="Sale Order")
    hq_category_id = fields.Many2one("inom.hq.category",string="Category")
    customer_id = fields.Many2one("res.partner", string="Customer/Patient")



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    custom_sale_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        compute="_compute_custom_sale_id",
        store=True,
    )

    @api.depends("order_line.custom_sale_id")
    def _compute_custom_sale_id(self):
        for order in self:
            sale = order.order_line.filtered(lambda l: l.custom_sale_id)[:1].custom_sale_id
            order.custom_sale_id = sale.id if sale else False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    custom_sale_id = fields.Many2one('sale.order',string="Sale Order")
    hq_category_id = fields.Many2one("inom.hq.category",string="Category")
    customer_id = fields.Many2one("res.partner", string="Customer/Patient")


    @api.onchange("custom_sale_id")
    def _onchange_custom_sale_id(self):
        for rec in self:
            if rec.custom_sale_id:
                # rec.hq_category_id = rec.partner_id.hq_category_id
                rec.customer_id = rec.custom_sale_id.partner_id.id
                




    def _prepare_account_move_line(self, move=False):
        values = super()._prepare_account_move_line(move=move)
        values['custom_sale_id']=self.custom_sale_id.id
        
        values['hq_category_id']=self.hq_category_id.id
        values['customer_id']=self.customer_id.id
        return values
