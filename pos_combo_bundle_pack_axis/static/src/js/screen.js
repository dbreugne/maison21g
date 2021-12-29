odoo.define('pos_combo_bundle_pack_axis.pos_screens', function (require) {
"use strict";

	var screens = require('point_of_sale.screens');

	screens.ProductScreenWidget.include({
		click_product: function(product) {
		    console.log(" ===================click_product", product)
        	this._super.apply(this, arguments);
        	var self = this;
        	var combo_products_details = [];
        	this.new_combo_products_details = [];
        	var order = self.pos.get_order();
        	var products_info = [];
        	var combo_list = [];
        	var products_info_1 = [];
        	product.pack_product_ids.map(function(id){
                var record = _.find(self.pos.product_combo, function(data){
                    return data.id === id;
                });
                combo_products_details.push(record);
            });
            console.log("combo_products_details---",combo_products_details)
            for (var key in combo_products_details) {
                    var product = self.pos.db.get_product_by_id(combo_products_details[key]['product_new_name_trial'][0]);
                    console.log("------------product-----",product)
                    products_info.push({
		                            "product":{
		                                'display_name':product.display_name,
		                                'id':product.id,
		                                'quantity':combo_products_details[key]['qty_new']
		                            },
		                        });
            }
            var selected_line = order.get_selected_orderline();
            if(products_info.length > 0 && selected_line){
            	selected_line.set_combo_prod_info(products_info);
            }
    	},
	});
});
