# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

from odoo import models, fields, api, _

class dev_pos_config(models.Model):
    _inherit = 'pos.config'
    
    load_pos_order = fields.Boolean(string='POS Orders', default=True)
    last_days = fields.Char("Last Days",default=120)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
