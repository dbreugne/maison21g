odoo.define('ms_pos_product_config.pos_model', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var DB = require('point_of_sale.DB');
    var QWeb = core.qweb;
    
    models.load_fields("product.product", ["is_scent", "is_bottle", "max_number_of_scents"]);
    
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            _super_orderline.initialize.apply(this, arguments);
            this.selected_scent = []
            this.engrave_line = options.engrave_line || false;
            this.scent_lines = options.scent_lines || [];
            this.remaining_scents = options.remaining_scents || 0;
            var product = options.product;
            if (product && product.is_bottle != false){
                this.pos.gui.show_popup('pos_perfume_configurator', {
                    bottle: product,
                    remaining_scents: product.max_number_of_scents,
                    bottle_name: product.display_name,
                    selected_scents: [],
                    bottle_order_line: this,
                });
            }
        },
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
            return res
        }
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
            this.product_scents = this.get_product_scent();
        },
        get_product_scent: function(){
            var res = {}
            _.forEach(this.product_by_id, function(product){
                if(product.is_scent){
                    res[product.id] = product      
                }
            })
            return res;
        }
    })
});