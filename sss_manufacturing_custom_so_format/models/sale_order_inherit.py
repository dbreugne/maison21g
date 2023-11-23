# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api,_
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
	_inherit = 'sale.order'

	mo_status = fields.Selection([('pending_manufacturing', 'Pending Manufacturing'), ('manufacturing_in_progress', 'Manufacturing in Progress'), ('ready_to_ship', 'Ready to Ship')], string="MO Status", copy=False, readonly=True)

	def action_confirm(self):
		res = super(SaleOrderInherit, self).action_confirm()
		for rec in self.order_line:
			for routes in rec.product_id.route_ids:
				if routes.name in ['Manufacture', 'Replenish on Order (MTO)']:
					rec.order_id.mo_status = 'pending_manufacturing'
		return res

class StockMove(models.Model):
	_inherit = 'stock.move'

	def unlink(self):
		if self.env.context.get('params'):
			if self.env.context.get('params').get('model') == 'mrp.production':
				try:
					return super(StockMove, self).unlink()
				except (UserError):
					if any(move.state in ('done','assigned') for move in self):
						raise UserError(_('You can only delete draft moves.'))
					self.state = "draft"
					return super(StockMove, self).unlink()
			else:
				return super(StockMove, self).unlink()
		else:
			return super(StockMove, self).unlink()
