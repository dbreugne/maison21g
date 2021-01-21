from odoo import api, fields, models 


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    po_number = fields.Many2one("purchase.order", string="PO")
