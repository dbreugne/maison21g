from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    owner_id = fields.Many2one('res.partner', string="Owner")
    serial_number = fields.Char(string="Serial NUmber")
    asset_location_id = fields.Many2one('account.asset.location', string="Location")

class AccountAssetLocation(models.Model):
    _name = "account.asset.location"
    _description = "Asset Location"
    
    name = fields.Char()