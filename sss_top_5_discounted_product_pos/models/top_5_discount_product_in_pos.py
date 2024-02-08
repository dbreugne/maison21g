# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class Top5DiscountProductInPOS(models.Model):
    _name = "top.discount.product.pos"
    _discreption = "Top 5 Discounted Product of POS"
    _auto = False

    name = fields.Char(string="Name")
    discount_rate = fields.Float(string='Discount Rate')
    product_id = fields.Many2one('product.product', string="Product")
    pos_order_id = fields.Many2one('pos.order', string="POS Order")
    config_id = fields.Many2one('pos.config', string="Point of Sales")

    def init(self):
        sql = '''
            WITH ranked_products AS (
                SELECT
                    pol.id,
                    pol.name,
                    pol.product_id AS product_id,
                    CASE
                        WHEN MAX(pol.discount + pos.amount_total) = 0 THEN 1
                        ELSE MAX(pol.discount) / (MAX(pol.discount) + SUM(pos.amount_total))
                    END AS discount_rate,
                    pc.id AS config_id,
                    pos.id AS pos_order_id,
                    ROW_NUMBER() OVER (PARTITION BY pc.id ORDER BY MAX(pol.discount) DESC) AS row_num
                FROM
                    pos_order_line AS pol
                LEFT JOIN
                    pos_order AS pos ON pol.order_id = pos.id
                LEFT JOIN
                    res_partner AS rp ON pos.partner_id = rp.id
                LEFT JOIN
                    pos_session AS ps ON ps.id = pos.session_id
                LEFT JOIN
                    pos_config AS pc ON pc.id = ps.config_id
                GROUP BY
                    pol.id, pc.id, pos.id, pol.product_id, pol.name
            )
            SELECT
                id,
                name,
                product_id,
                discount_rate,
                config_id,
                pos_order_id
            FROM
                ranked_products
            WHERE
                row_num <= 5
        '''
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table, sql)
        )
