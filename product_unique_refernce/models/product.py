from odoo import models,fields,api,_
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char('Internal Reference', index=True, copy=False)

    _sql_constraints = [('unique_default_code', 'UNIQUE(default_code)', 'Internal Reference Code must be unique')]

    @api.constrains('default_code')
    def _check_default_code(self):
        code = self.search([('default_code', '=', self.default_code)])
        if len(code) > 1:
            raise ValidationError(_("Internal Reference Code must be unique"))


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):  # pylint: disable=W0622

        if not default:
            default = {}

        default[
            'default_code'] = self.default_code and\
            self.default_code + ' (copy)' or False
        product = super(ProductTemplate, self).copy(default)
        return product

class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char('Internal Reference', index=True,copy=False)
    def copy(self, default=None):  # pylint: disable=W0622

        if not default:
            default = {}

        default[
            'default_code'] = self.default_code and\
            self.default_code + ' (copy)' or False

        return super(ProductProduct, self).copy(default=default)


