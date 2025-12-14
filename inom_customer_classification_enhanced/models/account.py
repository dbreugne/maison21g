from odoo import models, fields,api

class AccountMove(models.Model):
    _inherit = "account.move"
    channel_id = fields.Many2one("inom.channel")
    category_id = fields.Many2one(
        "inom.category",
        domain="[('channel_id','=',channel_id)]"
    )
    subcategory_id = fields.Many2one(
        "inom.subcategory",
        domain="[('category_id','=',category_id)]"
    )

    @api.onchange("partner_id")
    def _onchange_partner_classification(self):
        if self.partner_id:
            self.channel_id = self.partner_id.custom_channel_id
            self.category_id = self.partner_id.custom_category_id
            self.subcategory_id = self.partner_id.subcategory_id

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    hq_category_id = fields.Many2one("inom.hq.category")
    customer_id = fields.Many2one("res.partner", string="Customer/Patient")
