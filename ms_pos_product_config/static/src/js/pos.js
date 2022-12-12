odoo.define('ms_pos_product_config.product_config', function(require){
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

	var PerfumeConfigWidget = PopupWidget.extend({
	    template:'ParfumeConfigWIdget',
	    show: function(options){
	        // var self = this;
	        this._super(options);
	        this.renderElement();
	    },

    });


	gui.define_popup({name:'pos_perfume_configurator', widget: PerfumeConfigWidget});

	var PerfumeConfigButton = screens.ActionButtonWidget.extend({
	    template: 'ParfumeConfigButton',
        events: {
            'click .button.back':  'click_back',
        },
	    button_click: function(){
	        var product  = this.pos.db.get_product_by_id(this.pos.config.wildcard_product_id[0]);
	        this.gui.show_popup('pos_perfume_configurator');
	    },
	});


	screens.define_action_button({
	    'name': 'perfumeconfigurator',
	    'widget': PerfumeConfigButton
	});

});