from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    
    finished_lot_number = fields.Char('Lot/Serial Number Ref', related="finished_lot_id.name", readonly=False)