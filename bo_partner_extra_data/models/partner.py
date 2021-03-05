# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """Member's detail."""

    _inherit = 'res.partner'
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('unisex', 'Unisex')], string='Gender')
    birthdate = fields.Date('Date of Birth')
