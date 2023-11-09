# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
	_inherit = "sale.order"

	def action_cancel(self):
		for rec in self.invoice_ids:
			if rec.state not in ('cancel'):
				raise ValidationError(_("Cancel all invoices and delivery orders to cancel the sales order"))

		for rec in self.picking_ids:
			if rec.state not in ('cancel'):
				raise ValidationError(_("Cancel all invoices and delivery orders to cancel the sales order"))

		res = super(SaleOrder, self).action_cancel()
		return res
