{
	"name" : "POS Order Discount Enahncement ",
	"version" : "17.0.0.0",
	"category" : "Point of Sale",
	"depends" : ['base','point_of_sale','pos_loyalty'],
	'summary': 'POS Order Discount Enahncement',
	

	'assets': {
        'point_of_sale._assets_pos': [
        	
        	('replace', 'pos_loyalty/static/src/overrides/models/pos_store.js', 'pe_discount_enahncement/static/src/app/store/models.js'),
        	'pe_discount_enahncement/static/src/app/store/Order.js',
        	('replace', 'pos_loyalty/static/src/overrides/components/product_screen/product_screen.js', 'pe_discount_enahncement/static/src/app/store/product_screen.js'),
        	
        ],
    },

	"auto_install": False,
	"installable": True,
}
