odoo.define('ms_pos_product_config.pos_model', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var DB = require('point_of_sale.DB');
    var QWeb = core.qweb;
    
    models.load_fields("product.product", ["is_scent", "is_bottle", "max_number_of_scents"]);
    models.load_fields("pos.order.line", ["bottle_line_id"]);
    
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            _super_orderline.initialize.apply(this, arguments);
            this.selected_scent = []
            this.engrave_line = options.engrave_line || false;
            this.scent_lines = options.scent_lines || [];
            this.remaining_scents = options.remaining_scents || 0;
            this.bottle_line_idx = false;
            var product = options.product;
            if (product && product.is_bottle != false){
                this.pos.gui.show_popup('pos_perfume_configurator', {
                    bottle: product,
                    remaining_scents: product.max_number_of_scents,
                    bottle_name: product.display_name,
                    selected_scents: [],
                    bottle_order_line: this,
                    // bottle_line_id : this.id
                });
            }
        },
        // set_bottle_line_id: function (bottle_line_id) {
        //     this.bottle_line_id = bottle_line_id;
        // },
        // get_bottle_line_id: function(bottle_line_id){
        //     return this.bottle_line_id;
        // },
        destroy: function(){
            var res = _super_orderline.destroy.apply(this, arguments);
            return res            
        },
        can_be_merged_with: function(orderline){
            var res = _super_orderline.can_be_merged_with.apply(this, arguments);

            var product = this.product;
            if(product && (product.is_bottle || product.scent)){
                return false;
            }

            var product = orderline.product;
            if(product && (product.is_bottle || product.scent)){
                return false;
            }

            // var bottle_line_id = orderline.bottle_line_id;
            // if (product && (bottle_line_id.bottle_line_id)) {
            //     return false
            // }
            return res
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.bottle_line_idx = this.bottle_line_idx;
            return json;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_orderline: function(line){
            _super_order.add_orderline.apply(this, arguments);
        },
        remove_orderline: function(line){
            var self = this
            _super_order.remove_orderline.apply(this, arguments);
            if(line.product && line.product.is_bottle){
                self.remove_orderline(line.engrave_line)
                _.forEach(line.scent_lines, function(scent_line){
                    self.remove_orderline(scent_line)
                })
            }
        },
        add_product: function(product, options){
            var res = _super_order.add_product.apply(this, arguments);
            return res
        }
    }); 

    DB.include({
        init: function(options){
            this._super.apply(this, arguments);
            this.product_scents = {};
        },
        add_products: function(products){
            this._super.apply(this, arguments);
            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                if(product.is_scent){
                    this.product_scents[product.id] = product;
                    // this.product_scents['bottle_line_id'] = product.bottle_line_id;
                }
            }
        }
    })
});