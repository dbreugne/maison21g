# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """Member's detail."""

    _inherit = 'res.partner'
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('unisex', 'Unisex')], string='Gender')
    birthdate = fields.Date('Date of Birth')

    married = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string='Married')
    date_wedding = fields.Date('Date of Wedding')
    children = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string='Children')
    no_children = fields.Integer('No.of Children')