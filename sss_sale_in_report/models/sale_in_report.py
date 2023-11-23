from odoo import fields, models, tools
from functools import lru_cache


class saleInReport(models.Model):
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

	# _depends = {
	# 	'point_of_sale': [
	# 		'x_studio_order_date', 'state'
	# 	],

	# }

	def init(self):
		sql = '''
		SELECT pol.id, pol.name, prod.id  AS product_id, 
		temp.categ_id AS product_category_id, 
		sum(pol.price_subtotal) AS sales_quantity, 
		sum(pos.amount_total) AS total_price,  
		sum(temp.list_price) AS actual_selling_price, 
		seg.id AS industry_id, 
		rp.id AS partner_id,
		ru.id AS user_id,
		u.id AS uom_id,
		pos.id AS pos_order_id,
		sum(pos.amount_total) AS total_revenue,
		ps.config_id AS pos_config_id,

		CASE
	        WHEN SUM(pol.qty * u.factor) = 0 THEN NULL
	        ELSE (SUM(pos.amount_total*pol.qty / CASE COALESCE(pol.qty, 0) WHEN 0 THEN 1.0 ELSE pol.qty END)/SUM(pol.qty * u.factor))
        END AS average_price
		FROM pos_order_line AS pol
		LEFT JOIN pos_order AS pos ON pos.id = pol.order_id
		LEFT JOIN product_product AS prod ON prod.id = pol.product_id
		LEFT JOIN product_template AS temp ON temp.id = prod.id
		LEFT JOIN res_partner AS rp ON rp.id = pos.partner_id
		LEFT JOIN res_partner_industry AS seg ON seg.id = rp.industry_id
		LEFT JOIN res_users AS ru ON ru.id = pos.user_id
		LEFT JOIN uom_uom AS u ON u.id = temp.uom_id
		LEFT JOIN pos_session AS ps ON ps.id = pos.session_id
		LEFT JOIN pos_config AS pc ON pc.id = ps.config_id
		GROUP BY pol.id, pos.id,  pol.name, prod.id, seg.id, rp.id, ru.id, temp.categ_id, u.id, ps.config_id
		'''

		tools.drop_view_if_exists(self._cr, self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW %s AS (
				%s
			)
		""" % (self._table,sql)
		)
