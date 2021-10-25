from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char('Internal Reference', index=True, copy=False)

    @api.constrains('default_code')
    def _check_default_code(self):
        if self.default_code:
            code = self.search([('default_code', '=', self.default_code)])
            if len(code) > 1:
                raise UserError(_("Internal Reference Code must be unique"))


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char('Internal Reference', index=True, copy=False)

