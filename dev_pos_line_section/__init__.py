# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintelle.com>).
#
##############################################################################
from . import models

from odoo.api import Environment, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    for rec in env['pos.order.line'].search([('product_id','=',False)]):
        rec.unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
