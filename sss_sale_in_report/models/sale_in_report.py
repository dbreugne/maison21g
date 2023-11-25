# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class SaleInReport(models.Model):
    _name = 'sale.in.reports'
    _auto = False

    name = fields.Char(string="Name")
    sales_quantity = fields.Float(string="Sales Quantity")
    total_revenue = fields.Float(string="Total Revenue")
    actual_selling_price = fields.Monetary(string="Actual Selling  Price")
    currency_id = fields.Many2one('res.currency',string='Currency')
    product_category_id = fields.Many2one('product.category', string="Product Category")
    product_id = fields.Many2one('product.product', string="Product")
    partner_id = fields.Many2one('res.partner', string="Partner")
    industry_id = fields.Many2one('res.partner.industry', string="Segment")
    total_price = fields.Monetary(string="Total Price")
    user_id = fields.Many2one('res.users', string="Users")
    pos_config_id = fields.Many2one('pos.config', string="Pos Config")
    average_price = fields.Float(string="Average Price")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    pos_order_id = fields.Many2one('pos.order', string="POS Order")

    def init(self):
        sql = '''
        SELECT pol.id, pol.name, prod.id  AS product_id, 
        temp.categ_id AS product_category_id,
        CASE 
            WHEN u.name = 'kg' THEN sum((pol.qty) * 1000)
            ELSE sum(pol.qty)
        END AS sales_quantity,
        sum(pos.amount_total) AS total_price,  
        sum(temp.list_price) AS actual_selling_price,   
        rp.industry_id AS industry_id, 
        rp.id AS partner_id,
        ru.id AS user_id,
        u.id AS uom_id,
        pos.id AS pos_order_id,
        sum(pol.price_subtotal) AS total_revenue,
        CASE
            WHEN sum(pol.qty) = 0 THEN 1
            ELSE sum(pol.price_subtotal)/sum(pol.qty)
          END AS average_price
        FROM pos_order_line AS pol
        LEFT JOIN pos_order AS pos ON pos.id = pol.order_id
        LEFT JOIN account_move AS am ON pos.account_move = am.id
        LEFT JOIN product_product AS prod ON prod.id = pol.product_id
        LEFT JOIN product_template AS temp ON temp.id = prod.id
        LEFT JOIN res_partner AS rp ON rp.id = pos.partner_id
        LEFT JOIN res_partner_industry AS seg ON seg.id = rp.industry_id
        LEFT JOIN res_users AS ru ON ru.id = pos.user_id
        LEFT JOIN uom_uom AS u ON u.id = temp.uom_id
        LEFT JOIN pos_session AS ps ON ps.id = pos.session_id
        LEFT JOIN pos_config AS pc ON pc.id = ps.config_id
        -- WHERE pos.partner_id IS NOT NULL
        GROUP BY pol.id, pos.id,  pol.name, prod.id, seg.id, rp.id, ru.id, temp.categ_id, u.id, ps.config_id

        UNION ALL
        SELECT air.id, air.name, prod.id  AS product_id, 
        temp.categ_id AS product_category_id,
        CASE 
            WHEN u.name = 'kg' THEN sum((air.quantity) * 1000)
            ELSE sum(air.quantity)
        END AS sales_quantity,
        sum(air.amount_total) AS total_price,  
        sum(temp.list_price) AS actual_selling_price,   
        rp.industry_id AS industry_id, 
        rp.id AS partner_id,
        air.invoice_user_id AS user_id,
        u.id AS uom_id,
        po.id AS pos_order_id,
        sum(air.price_subtotal) AS total_revenue,
        CASE
            WHEN sum(air.quantity) = 0 THEN 1
            ELSE sum(air.price_subtotal)/sum(air.quantity)
          END AS average_price
        FROM account_invoice_report AS air
        LEFT JOIN account_move AS am ON am.id = air.move_id
        LEFT JOIN pos_order AS po ON po.id = am.pos_order_id
        LEFT JOIN res_partner AS rp ON rp.id = air.partner_id
        LEFT JOIN product_product AS prod ON prod.id = air.product_id
        LEFT JOIN product_template AS temp ON temp.id = prod.id
        LEFT JOIN uom_uom AS u ON u.id = air.product_uom_id
        LEFT JOIN res_partner_industry AS seg ON seg.id = rp.industry_id
        GROUP BY air.id, air.id,  air.name, prod.id, seg.id, rp.id, air.invoice_user_id, temp.categ_id, u.id, po.id
        '''

        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table,sql)
        )


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        response = super(SaleInReport, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        for rec in response:
            if 'total_revenue' in rec and 'sales_quantity' in rec:
                rec['average_price'] = rec.get('total_revenue') / rec.get('sales_quantity') if rec.get('sales_quantity') else 1
        return response


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_order_id = fields.Many2one('pos.order', string="Pos Order")
