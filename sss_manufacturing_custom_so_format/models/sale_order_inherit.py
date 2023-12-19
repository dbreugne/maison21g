# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    mo_status = fields.Selection([('pending_manufacturing', 'Pending Manufacturing'), ('manufacturing_in_progress',
                                 'Manufacturing in Progress'), ('ready_to_ship', 'Ready to Ship'), ('partially_under_manufacturing', 'Partially Under Manufacturing'), ('partially_manufactured', 'Partially Manufactured'), ('cancel', 'Cancel Manufacturing')], string="MO Status", copy=False, readonly=True)
    manufacturing_count = fields.Integer(
        string="Manufacturing Order", compute="_compute_manufacturing_count", copy=False)
    manufacturing_ids = fields.Many2many('mrp.production', 'manufacturing_order_type',
                                         'saleorder_id', 'mrpproduction_id', string='Manufacturing Orders', copy=False)

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        for rec in self.order_line:
            routes = []
            route_ids = self.env['stock.location.route'].search([('name', '=', 'Replenish on Order (MTO)')])
            route_idss = self.env['stock.location.route'].search([('name', '=', 'Manufacture')])
            route_idsss = self.env['stock.location.route'].search([('name', '=', 'Buy')])
            routes.append(route_ids.id)
            routes.append(route_idss.id)
            if routes == rec.product_id.route_ids.ids and rec.available_qty <= rec.product_uom_qty:
                rec.order_id.mo_status = 'pending_manufacturing'
            elif rec.available_qty <= rec.product_uom_qty and rec.product_id.bom_ids and routes != rec.product_id.route_ids.ids:
                mo_values = {
                    'origin': self.name,
                    'product_id': rec.product_id.id,
                    'product_qty': rec.product_uom_qty,
                    'product_uom_id': rec.product_uom.id,
                    'bom_id': rec.product_id.bom_ids.id,
                    'date_deadline': self.date_order,
                    'date_planned_finished': self.date_order,
                    'date_planned_start': self.date_order,
                    'procurement_group_id': False,
                    'propagate_date': self.date_order,
                    'company_id': self.company_id.id,
                    'user_id': False,
                }
                mrp_id = self.env['mrp.production'].create(mo_values)
                mrp_id._onchange_move_raw()
                mrp_id._onchange_location()
                mrp_id.action_confirm()
                rec.order_id.mo_status = 'pending_manufacturing'
        return res

    @api.depends('manufacturing_ids')
    def _compute_manufacturing_count(self):
        for order in self:
            order.manufacturing_count = len(order.manufacturing_ids)

    def action_cancel(self):
        res = super(SaleOrderInherit, self).action_cancel()
        if self.manufacturing_ids:
            for mrp in self.manufacturing_ids:
                mrp.write({'state': 'cancel'})
                mrp.sale_id.mo_status = 'cancel'
                for sale in mrp.move_raw_ids:
                    sale.state = 'cancel'
        return res

    def action_view_manufacturing(self):
        self.ensure_one()
        return {

            'name': 'Manufacturing Orders',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', self.manufacturing_ids.ids)],
            'context': {'is_mrp_production': True},
            'type': 'ir.actions.act_window'
        }


class StockMove(models.Model):
    _inherit = 'stock.move'

    def unlink(self):
        if self.env.context.get('is_mrp_production'):
            try:
                return super(StockMove, self).unlink()
            except (UserError):
                if any(move.state in ('done', 'assigned') for move in self):
                    raise UserError(_('You can only delete draft moves.'))
                self.state = "draft"
                return super(StockMove, self).unlink()
        else:
            return super(StockMove, self).unlink()
