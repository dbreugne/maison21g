# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_id = fields.Many2one('sale.order', string="Sale Order", copy=False)
    order_count = fields.Integer(string="Sale Order", compute="_compute_order_count", copy=False)
    lot_id = fields.Many2one('stock.lot', string="Lot Number")
    expiry_date = fields.Date(string="Expiry Date")

    @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id')
    def _onchange_move_raw(self):
        # Clear move raws if we are changing the product. In case of creation (self._origin is empty),
        # we need to avoid keeping incorrect lines, so clearing is necessary too.
        if self.product_id != self._origin.product_id:
            self.move_raw_ids = [(5,)]
        if self.bom_id and self.product_qty > 0:
            # keep manual entries
            list_move_raw = [(4, move.id) for move in self.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
            moves_raw_values = self._get_moves_raw_values()
            move_raw_dict = {move.bom_line_id.id: move for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)}
            for move_raw_values in moves_raw_values:
                if move_raw_values['bom_line_id'] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                else:
                    # add new entries
                    list_move_raw += [(0, 0, move_raw_values)]
            self.move_raw_ids = list_move_raw
        else:
            self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)]

    @api.onchange('location_src_id', 'move_raw_ids', 'routing_id')
    def _onchange_location(self):
        source_location = self.location_src_id
        self.move_raw_ids.update({
            'warehouse_id': source_location.warehouse_id.id,
            'location_id': source_location.id,
        })

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        location = self.env.ref('stock.stock_location_stock')
        self.move_raw_ids.update({'picking_type_id': self.picking_type_id})
        self.location_src_id = self.picking_type_id.default_location_src_id.id or location.id
        self.location_dest_id = self.picking_type_id.default_location_dest_id.id or location.id

    def _compute_order_count(self):
        for order in self:
            order.order_count = len(order.sale_id)


    def action_view_saleorder(self):
        self.ensure_one()
        return {
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', '=', self.sale_id.id)],
            'context': {'is_mrp_production': True},
            'type': 'ir.actions.act_window'
        }

    @api.model
    def create(self, values):
        res = super(MrpProduction, self).create(values)
        sale_id = self.env['sale.order'].search([('name', '=', values.get('origin', ''))], limit=1)
        res['sale_id'] = sale_id.id
        if sale_id:
            sale_id.write({
                'manufacturing_ids': [(4, res.id)]
                })
        return res

    def open_produce_product(self):
        res = super(MrpProduction, self).open_produce_product()
        mrp_ids = self.search([('origin', '=', self.sale_id.name), ('state', '=', 'confirmed')])
        product_uom_qty = sum(self.move_raw_ids.filtered(lambda x: x.product_uom_qty).mapped('product_uom_qty'))
        reserved_availability = sum(self.move_raw_ids.filtered(lambda x: x.reserved_availability).mapped('reserved_availability'))
        if product_uom_qty != reserved_availability:
            raise UserError(_("You cannot Start Production for this Finished Goods because Don't have sufficient Raw Material. if no quantites are reserved nor done."))
            # raise UserError(_('You cannot Start Production a Manufacturing Raw Material if no quantites are reserved nor done.'))
        if len(mrp_ids.ids) == 1:
            mrp_ids.sale_id.mo_status = 'manufacturing_in_progress'
        else:
            mrp_ids.sale_id.mo_status = 'partially_under_manufacturing'
        return res

    def button_mark_done(self):
        mrp_ids = self.search([('origin', '=', self.sale_id.name), '|', ('state', '=', 'to_close'),  ('state', '=', 'confirmed')])
        if len(mrp_ids.ids) == 1:
            mrp_ids.sale_id.mo_status = 'ready_to_ship'
        else:
            mrp_ids.sale_id.mo_status = 'partially_manufactured'
        res = super(MrpProduction, self).button_mark_done()
        return res

# now this objects are not available in the v-17

# class MrpProductProduce(models.TransientModel):
#     _inherit = 'mrp.product.produce'
#
#     expairy_date = fields.Date('Expiry Date')
#
#     @api.model
#     def default_get(self, fields):
#         res = super(MrpProductProduce, self).default_get(fields)
#         current_date = datetime.now()
#         three_years_later = current_date + relativedelta(years=3)
#         # mrp_seq = self.env['ir.sequence'].next_by_code('stock.production.lot.mrp')
#         current_year = datetime.now().year
#         # current_month = datetime.now().month
#         current_month = datetime.now().strftime('%B')
#         current_months = ''
#         if current_month == 'January':
#             current_months = 'A'
#         elif current_month == 'February':
#             current_months = 'B'
#         elif current_month == 'March':
#             current_months = 'C'
#         elif current_month == 'April':
#             current_months = 'D'
#         elif current_month == 'May':
#             current_months = 'E'
#         elif current_month == 'June':
#             current_months = 'F'
#         elif current_month == 'July':
#             current_months = 'G'
#         elif current_month == 'August':
#             current_months = 'H'
#         elif current_month == 'Seprember':
#             current_months = 'I'
#         elif current_month == 'October':
#             current_months = 'J'
#         elif current_month == 'November':
#             current_months = 'K'
#         elif current_month == 'December':
#             current_months = 'L'
#         lst = str(current_year)[-1] + current_months + str(datetime.now().date())[-2:]
#         product_id = self.env['product.product'].browse(res.get('product_id'))
#         if product_id.tracking == 'lot':
#             lot_ids = self.env['stock.production.lot'].search([('name', '=', lst), ('product_id', '=', res.get('product_id'))], limit=1)
#             if not lot_ids:
#                 lot_id = self.env['stock.production.lot'].create({
#                     'product_id': res.get('product_id'),
#                     'product_qty': res.get('qty_producing'),
#                     'product_uom_id': res.get('product_uom_id'),
#                     'company_id': self.env.company.id,
#                     'life_date': three_years_later,
#                     'name': lst})
#                 res['finished_lot_id'] = lot_id.id
#             else:
#                 res['finished_lot_id'] = lot_ids.id
#
#         res['expairy_date'] = three_years_later
#         return res
#
#     def do_produce(self):
#         res = super(MrpProductProduce, self).do_produce()
#         # self._context.get('active_id')
#         mrp_production = self.env['mrp.production'].browse(self._context.get('active_id'))
#         if mrp_production.product_id.tracking == 'lot':
#             mrp_production.lot_id = self.finished_lot_id.id
#             self.production_id.move_finished_ids.move_line_ids.lot_id = self.finished_lot_id.id
#             self.production_id.sale_id.lot_ids = [(4, self.finished_lot_id.id)]
#         mrp_production.expiry_date = self.expairy_date
#         self.production_id.sale_id.expiry_date = self.expairy_date
#         return res
#
#     def _record_production(self):
#         if self.product_id.tracking == 'lot':
#             self.production_id.move_finished_ids.move_line_ids.lot_id = self.finished_lot_id.id
#         res = super(MrpProductProduce, self)._record_production()
#         return res

#
# class MrpAbstractWorkorder(models.AbstractModel):
#     _inherit = "mrp.abstract.workorder"
#
#     def _update_workorder_lines(self):
#         res = super(MrpAbstractWorkorder, self)._update_workorder_lines()
#         current_date = datetime.now()
#         three_years_later = current_date + relativedelta(years=3)
#         # mrp_seq = self.env['ir.sequence'].next_by_code('stock.production.lot.mrp')
#
#         current_year = datetime.now().year
#         # current_month = datetime.now().month
#         current_month = datetime.now().strftime('%B')
#         current_months = ''
#         if current_month == 'January':
#             current_months = 'A'
#         elif current_month == 'February':
#             current_months = 'B'
#         elif current_month == 'March':
#             current_months = 'C'
#         elif current_month == 'April':
#             current_months = 'D'
#         elif current_month == 'May':
#             current_months = 'E'
#         elif current_month == 'June':
#             current_months = 'F'
#         elif current_month == 'July':
#             current_months = 'G'
#         elif current_month == 'August':
#             current_months = 'H'
#         elif current_month == 'Seprember':
#             current_months = 'I'
#         elif current_month == 'October':
#             current_months = 'J'
#         elif current_month == 'November':
#             current_months = 'K'
#         elif current_month == 'December':
#             current_months = 'L'
#         lst = str(current_year)[-1] + current_months + str(datetime.now().date())[-2:]
#         for rec in res.get('to_create'):
#             lot_ids = self.env['stock.production.lot'].search([('name', '=', lst), ('product_id', '=', rec.get('product_id'))], limit=1)
#             product_id = self.env['product.product'].browse(rec.get('product_id'))
#             if product_id.tracking == 'lot':
#                 if not lot_ids:
#                     lot_id = self.env['stock.production.lot'].create({
#                         'product_id': rec.get('product_id'),
#                         'product_qty': rec.get('qty_done'),
#                         'product_uom_id': rec.get('product_uom_id'),
#                         'company_id': self.env.company.id,
#                         'life_date': three_years_later,
#                         'name': lst})
#
#                     rec.update({'lot_id': lot_id.id})
#                 else:
#                     rec.update({'lot_id': lot_ids.id})
#         return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_id = fields.Many2one('sale.order', string="Sale Order", copy=False)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.depends('picking_id.picking_type_id', 'product_id.tracking')
    def _compute_lots_visible(self):
        res = super(StockMoveLine, self)._compute_lots_visible()
        if self.lot_id:
            self.lots_visible = True
        return res
