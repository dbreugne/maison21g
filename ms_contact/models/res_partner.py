# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    industry_id = fields.Many2one('res.partner.industry', 'Segment', required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get('industry_id', 0):
            res.update({'industry_id': ''})
        return res
