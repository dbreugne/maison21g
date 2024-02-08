# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_order_id = fields.Many2one('pos.order', string="Pos Orders")


class CRMTeam(models.Model):
	_inherit = 'crm.team'

	industry_id = fields.Many2one('res.partner.industry', string="Segment")
