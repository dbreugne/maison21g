from odoo import models,fields,api,_
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char('Internal Reference', index=True, copy=False)

    _sql_constraints = [('unique_default_code', 'UNIQUE(default_code)', 'Internal Reference Code must be unique')]
    # @api.model
    # def create(self, vals):
    #     res=
    @api.constrains('default_code')
    def _check_default_code(self):
        code = self.search([('default_code', '=', self.default_code)])
        if len(code) > 1:
            raise ValidationError(_("Internal Reference Code must be unique"))

    def copy(self, default=None):  # pylint: disable=W0622

        if not default:
            default = {}

        default[
            'default_code'] = self.default_code and\
            self.default_code + ' (copy)' or False

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

    # _sql_constraints = [

    #     ('default_code_unique', 'unique (default_code)',
    #      'The code of Product must be unique !'),
    # ]



