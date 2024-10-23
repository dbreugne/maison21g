from odoo import api, fields, models 


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    po_number = fields.Many2one("purchase.order", string="PO Num")


    def button_print_delivery(self):
        return self.env.ref('delivery_report_modifications.action_report_delivery_new').report_action(self)
