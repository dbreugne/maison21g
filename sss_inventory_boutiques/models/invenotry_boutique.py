from odoo import models, fields, api, _
from odoo import tools


class InventoryBoutiques(models.Model):
	_name = "inventory.boutiques"
	_auto = False
	_description = "Inventory - Boutiques"

	order_id = fields.Many2one('pos.order', 'POS Order')
	picking_id = fields.Many2one('stock.picking', 'Picking')
	product_id = fields.Many2one('product.product', 'Product')
	location_id = fields.Many2one('stock.location', 'Location')
	warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
	internal_ref = fields.Char('SKU')
	user_id = fields.Many2one('res.users', 'Users')
	uom_id = fields.Many2one('uom.uom', 'UOM')
	available_qty = fields.Float('Product Qty')

	def init(self):
		# sql = '''
		# SELECT pol.id, pol.product_id as product_id, sl.id as location_id, sw.id as warehouse_id, pp.default_code as internal_ref, pos.id as order_id, sp.id as picking_id, pol.qty as available_qty
		# from pos_order_line AS pol
		# LEFT JOIN pos_order AS pos ON pos.id = pol.order_id
		# LEFT JOIN stock_picking AS sp ON sp.id = pos.picking_id
		# LEFT JOIN stock_location AS sl ON sl.id = sp.location_id
		# LEFT JOIN stock_warehouse AS sw ON sw.lot_stock_id = sl.id
		# LEFT JOIN product_product AS pp ON pol.product_id = pp.id
		# WHERE sw.active = '''+str(True)+'''
		# '''

		sql = '''
			SELECT sm.id, pos.id AS order_id, sm.product_id AS product_id, sp.id AS picking_id, sl.id AS location_id, sw.id AS warehouse_id, pp.default_code AS internal_ref, sm.product_uom_qty AS available_qty
			FROM pos_order AS pos 
			LEFT JOIN stock_picking AS sp ON sp.id = pos.picking_id
			LEFT JOIN stock_location AS sl ON sl.id = sp.location_id
			LEFT JOIN stock_warehouse AS sw ON sw.lot_stock_id = sl.id
			LEFT JOIN stock_move AS sm ON sm.picking_id = sp.id
			LEFT JOIN product_product AS pp ON sm.product_id = pp.id
			WHERE sw.id in '''+str(tuple([39, 1, 36]))+''' AND sp.state in '''+str(('draft', 'waiting', 'confirmed'))+'''
		'''

		tools.drop_view_if_exists(self._cr, self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW %s AS (
				%s
			)
		""" % (self._table, sql)
		)
