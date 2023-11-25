# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_id = fields.Many2one('sale.order', string="Sale Order Ref")

    @api.model
    def create(self, values):
        res = super(MrpProduction, self).create(values)
        # context = self.env.context
        sale_id = self.env['sale.order'].search([('name', '=', values.get('origin',''))], limit=1)
        res['sale_id'] = sale_id.id
        if sale_id:
            sale_id.write({
                'manufacturing_ids': [(6,0,res.ids)]
                })
        return res

    def open_produce_product(self):
        res = super(MrpProduction, self).open_produce_product()
        mrp_ids = self.search([('origin','=', self.sale_id.name),('state','=', 'confirmed')])
        if len(mrp_ids.ids) == 1:
            mrp_ids.sale_id.mo_status = 'manufacturing_in_progress'
        return res

    def button_mark_done(self):
        mrp_ids = self.search([('origin','=', self.sale_id.name),('state','=', 'to_close')])
        if len(mrp_ids.ids) == 1:
            mrp_ids.sale_id.mo_status = 'ready_to_ship'
        res = super(MrpProduction, self).button_mark_done()
        return res




class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    expairy_date = fields.Datetime('Expairy Date')

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        current_date = datetime.now()
        three_years_later = current_date + relativedelta(years=3)
        if res.get('product_id'):
            lot_id = self.env['stock.production.lot'].create({
                'product_id': res.get('product_id'),
                'product_qty': res.get('qty_producing'),
                'product_uom_id': res.get('product_uom_id'),
                'company_id': self.env.company.id,
                'life_date': three_years_later,
                'name': self.env['ir.sequence'].next_by_code('stock.production.lot.seial')})
            res['finished_lot_id'] = lot_id.id
            res['expairy_date'] = three_years_later
        return res
