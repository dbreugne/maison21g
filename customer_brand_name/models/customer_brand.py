from odoo import models, fields

class CustomerBrand(models.Model):
    _name = 'customer.brand'
    _description = 'Customer Brand'

    name = fields.Char(string="Brand Name", required=True)

