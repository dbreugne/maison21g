from odoo import models, fields, api
from odoo import tools
from functools import lru_cache

class saleInReport(models.Model):
	_name = 'sale.in.report'
	_auto = False
	_order = 'order_date asc'

	sales_quantity = fields.Float(string="Sales Quantity")
	total_revenue = fields.Float(string="Total Revenue")
	actual_selling_price = fields.Monetary(string="Actual Selling  Price")
	currency_id = fields.Many2one('res.currency')
	product_category_id = fields.Many2one('product.category', string="Product Category")
	product_id = fields.Many2one('product.product', string="Product")
	partner_id = fields.Many2one('res.partner', string="Partner")
	industry_id = fields.Many2one('res.partner.industry', string="Segment")
	total_price = fields.Monetary(string="Total Price")
	total_discount = fields.Float(string="Total Discount")
	user_id =fields.Many2one('res.users', string="Segment")

	_depends = {
		'point_of_sale': [
			'x_studio_order_date', 'state'
		],

	}

	def init(self):

		# sql = '''
		# 	SELECT l.id,l.name, sum(l.sales_quantity) as sales_quantity, seg.id AS industry_id, count(s.id) AS actual_selling_price,cat.id AS product_category_id, s.x_studio_order_date AS order_date,s.state AS state,rp.id AS partner_id
		# 	FROM pos_order_line AS l
		# 	LEFT JOIN pos_order AS s ON s.id = l.order_id
		# 	LEFT JOIN res_partner AS rp ON rp.id = s.partner_id
		# 	LEFT JOIN product_category AS cat ON cat.id = l.product_category_id
		# 	WHERE s.invoice_status in ('invoiced','to invoice','upselling')
		# 	GROUP BY l.id,seg.id,s.id,rp.id,s.x_studio_order_date
		# 	ORDER BY s.x_studio_order_date ASC
		#  '''

		sql = '''
		SELECT pol.id, pol.product_id as product_id
		from pos_order_line AS pol
		LEFT JOIN product_product AS prod ON prod.id = pol.product_id
		LEFT JOIN product_category AS categ ON categ.id = prod.categ_id
		'''

		tools.drop_view_if_exists(self._cr, self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW %s AS (
				%s
			)
		""" % (self._table,sql)
		)

