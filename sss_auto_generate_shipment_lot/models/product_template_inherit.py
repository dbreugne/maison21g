# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import random


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    is_liquid = fields.Boolean(string="Is Liquid")


class StockMove(models.Model):
    _inherit = "stock.move"

    is_true_lot = fields.Boolean('Is Lot')

    def action_show_details(self):
        res = super().action_show_details()
        # my_id = self.browse(res["res_id"])
        if not self.product_id.is_liquid and self.product_id.tracking == 'lot' and not self.is_true_lot and self.picking_id.picking_type_id.code == 'incoming':
            self.write({"move_line_nosuggest_ids": [(0,0, {
                'product_id': self.product_id.id,
                'qty_done': self.product_qty,
                'product_uom_id': self.product_uom.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_id': self.picking_id.id,
                'company_id': self.company_id.id,
                'lot_name': self.env['ir.sequence'].next_by_code('stock.production.lot.seial')})]})
            self.is_true_lot = True
        return res
