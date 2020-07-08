
from . import models

from odoo.api import Environment, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    for rec in env['pos.order.line'].search([('product_id','=',False)]):
        rec.unlink()

