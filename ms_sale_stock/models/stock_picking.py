from odoo import api, fields, models, _


SHIPPING_BOX_SELECTION = [
    ('square', 'Square'),
    ('small', 'Small'),
    ('medium', 'Medium'),
    ('large', 'Large'),
]
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_box = fields.Selection(SHIPPING_BOX_SELECTION)
    