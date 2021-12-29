odoo.define('pos_combo_bundle_pack_axis.load_product_models', function (require) {
"use strict";
	var models = require('point_of_sale.models');
	models.load_fields("product.product", ['is_product_pack', 'pack_product_ids']);

	models.PosModel.prototype.models.push({
        model:  'pack.product',
        loaded: function(self,product_combo){
            self.product_combo = product_combo;
        },
    });
	var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

    	initialize: function(attr,options){
            _super_orderline.initialize.call(this, attr, options);
            this.combo_prod_info = false;
        },
        set_combo_prod_info: function(combo_prod_info){
            this.combo_prod_info = combo_prod_info;
            this.trigger('change',this);
        },
        get_combo_prod_info: function(){
            console.log("------------------get_combo_prod_nfo---")
            return this.combo_prod_info;
        },
        export_for_printing: function(){
            var self = this;
            var receipt = _super_orderline.export_for_printing.call(this);
            receipt['get_combo_prod_info'] = self.get_combo_prod_info() || false;
            return receipt;
        },
    });
});