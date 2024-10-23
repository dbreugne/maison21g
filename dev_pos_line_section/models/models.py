from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class dev_pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    product_id = fields.Many2one('product.product', string='Product', required=False, domain=[('sale_ok', '=', True)],
                                 change_default=True)
    name = fields.Char(string="Name")
    display_type = fields.Selection([('line_section', 'Section')], default=False, string="Display Type")

    @api.model_create_multi
    def create(self, values):
        for data in values:
            if data.get('display_type', self.default_get(['display_type'])['display_type']):
                data.update(product_id=False, price_unit=0, qty=0)
        return super(dev_pos_order_line, self).create(values)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_widcard = fields.Boolean(string='Section')
    wildcard_product_id = fields.Many2one('product.product', string='Section Product',
                                          domain="[('available_in_pos', '=', True), ('is_widcard', '=', True)]")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    iface_widcard = fields.Boolean(related='pos_config_id.iface_widcard',readonly=False)
    wildcard_product_id = fields.Many2one(related='pos_config_id.wildcard_product_id',readonly=False)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_widcard = fields.Boolean(string="Used as Section")


class Product(models.Model):
    _inherit = 'product.product'

    is_widcard = fields.Boolean(string="Used as Section")

    @api.model
    def update_product_name(self, values):
        if values.get('product_id') and values.get('name') and values.get('price'):
            self.browse(values.get('product_id')).write({'name': values.get('name'), 'lst_price': values.get('price')})
        return True


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['is_widcard'])
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: