# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    address = fields.Text(string="Address")


class SaleOrder(models.Model):
	_inherit = "sale.order"

	address = fields.Text(string="Address")
	