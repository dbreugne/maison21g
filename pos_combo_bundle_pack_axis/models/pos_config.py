from odoo import models, fields


class pos_config(models.Model):
    _inherit = "pos.config"

    bundle_print_type = fields.Selection([('print_only_bundle_product_on_receipt',"Print Only Bundle Product on Receipt"),
                                          ('print_bundle_and_bundle_item_both_on_receipt',"Print Bundle and Bundle Item Both on Receipt")],default='print_only_bundle_product_on_receipt')