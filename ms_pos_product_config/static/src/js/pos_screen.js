odoo.define('ms_pos_product_config.screen', function(require){
    'use strict';

    var screen = require('point_of_sale.screens');

    var _super_orderwidget = screen.OrderWidget.prototype;
    screen.OrderWidget.include({
        render_orderline: function(orderline){
            var res = this._super(orderline)
            // var el_str  = QWeb.render('Orderline',{widget:this, line:orderline}); 
            // var el_node = document.createElement('div');
            //     el_node.innerHTML = _.str.trim(el_str);
            //     el_node = el_node.childNodes[0];
            //     el_node.orderline = orderline;
            //     el_node.addEventListener('click',this.line_click_handler);
            var parfume_config = res.querySelector('.js_parfume_config');
            var product = orderline.product
            if(product && product.is_bottle && parfume_config){
                parfume_config.addEventListener('click', (function() {
                    this.pos.gui.show_popup('pos_perfume_configurator', {
                        bottle: product,
                        remaining_scents: (product) ? product.max_number_of_scents - orderline.scent_lines.length : 0,
                        bottle_name: (product) ? product.display_name : '',
                        section_name: (orderline.engrave_line && orderline.engrave_line.product) ? orderline.engrave_line.product.display_name : '',
                        // selected_scents: [],
                        bottle_order_line: orderline,
                    });
                }.bind(this)));
            }
    
            // orderline.node = el_node;
            return res;
        },
    });
});