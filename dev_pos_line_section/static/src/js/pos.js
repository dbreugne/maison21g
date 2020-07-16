odoo.define('dev_pos_line_section.pos', function (require) {
	"use strict";

	var screens = require('point_of_sale.screens');
	var models = require('point_of_sale.models');
	var PopupWidget = require('point_of_sale.popups');
	var gui = require('point_of_sale.gui');
	var core = require('web.core');
	var config = require('web.config');
	var rpc = require('web.rpc');
	var QWeb = core.qweb;
	var _t = core._t;

	models.load_fields('product.product',['is_widcard']);

	var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
    	set_is_section_product: function(){
    		this.display_type = 'line_section'
    	},
    	get_is_section_product: function(){
    		return this.display_type;
    	},
    	set_section_name: function(name){
        	this.section_name = name;
        },
        get_section_name: function(){
        	return this.section_name;
        },
        export_for_printing: function(){
        	var self = this;
            var lines = _super_orderline.export_for_printing.call(this);
            lines.product = this.product;
            lines.name = this.get_section_name() || '';
            return lines;
        },
        export_as_JSON: function() {
            var self = this;
            var lines = _super_orderline.export_as_JSON.call(this);
            lines.name = this.get_section_name() || '';
            lines.display_type = this.get_is_section_product() || false;
            return lines
        },
        init_from_JSON: function(json) {
        	_super_orderline.init_from_JSON.apply(this, arguments);
            var self = this;
            this.name = json.section_name;
            this.display_type = this.display_type;
        },
    });
	
	var WildCardWidget = PopupWidget.extend({
	    template:'WildCardWidget',
	    show: function(options){
	        var self = this;
	        this._super(options);
	        this.renderElement();
	    },
	    click_confirm: function(){ 
	        var self          = this;
	        var product_name  = this.$('.product_name').val();
	        if(!product_name){
	        	return alert(_t("Enter Section Name"));
	        }
	        var id            = self.pos.config.wildcard_product_id[0];
	        var product       = self.pos.db.get_product_by_id(id);
	        var order = self.pos.get_order();
	        var line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
	        line.set_quantity(0);
            line.set_unit_price(0);
            line.set_is_section_product(true);
            line.set_section_name(product_name);
            order.add_orderline(line);
	        self.gui.close_popup();
	    },
	});

	gui.define_popup({name:'pos_wildcard', widget: WildCardWidget});

	var WildCardButton = screens.ActionButtonWidget.extend({
	    template: 'WildCardButton',
	    button_click: function(){
	        var product  = this.pos.db.get_product_by_id(this.pos.config.wildcard_product_id[0]);
	        if (!product) {
	            this.gui.show_popup('error', {
	                title : _t("No section product found"),
	                body  : _t("The section product seems misconfigured. Make sure it is flagged as 'Use as section' and 'Available in Point of Sale'."),
	            });
	            return;
	        }
	        this.gui.show_popup('pos_wildcard');
	    },
	});

	screens.define_action_button({
	    'name': 'wildcard',
	    'widget': WildCardButton,
	    'condition': function(){
	        return this.pos.config.iface_widcard && this.pos.config.wildcard_product_id;
	    },
	});

});
