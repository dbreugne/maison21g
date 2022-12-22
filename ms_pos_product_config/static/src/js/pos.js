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
			this.remaining_scents = options.remaining_scents;
			this.bottle_order_line = options.bottle_order_line || false;
			this.section_order_line = options.section_order_line || false;
			this.scent_order_lines = options.scent_order_lines || [];
			this.selected_scents = options.selected_scents || [];
			this.bottle_name = options.bottle_name || '';
			this.section_name = options.section_name || '';
	        this.renderElement();
	    },
        click_confirm: function(){
			var self = this
            var section_name = this.$('input.section_name').val();
			var id = self.pos.config.wildcard_product_id[0];
	        var product = self.pos.db.get_product_by_id(id);
	        var order = self.pos.get_order();
	        var section_line = new models.Orderline({}, {pos: this.pos, order: order, product: product});
	        section_line.set_quantity(0);
            section_line.set_unit_price(0);
            section_line.set_is_section_product(true);
            section_line.set_section_name(section_name);

			// get indexof bottle
			var idx = order.orderlines.indexOf(this.bottle_order_line);
			// add section name before bottle
			order.orderlines.add(section_line, {at: idx - 1})
			this.bottle_order_line.engrave_line = section_line

			var scent_id;
			$('input[name^="scent"]').map(function(){
				var value = $(this).val()
				if($(this).hasClass('scent_id')){
					scent_id = parseInt(value)
				}
				if($(this).hasClass('scent_qty')){
					idx+=2;
					var scent_qty = parseFloat(value)
					var product = self.pos.db.get_product_by_id(scent_id);
					var scent_line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
					scent_line.set_quantity(scent_qty);
					scent_line.set_unit_price(product.get_price(order.pricelist, scent_qty));
					self.bottle_order_line.scent_lines.push(scent_line)
					order.orderlines.add(scent_line, {at: idx});
					self.bottle_order_line -= 1;
					console.log(scent_line)
				}
			}).get();
			
			this.gui.close_popup();
            // if( this.options.confirm ){
            //     this.options.confirm.call(this,value);
            // }
        },
		renderElement: function(){
			var self = this;
			this._super();
			this.$('#add_scent').click(function(event){
				self.add_scent_handler(event,$(this));
			});
			$('input[name^="scent"]').change(function(event) {
				self.onchange_scent_handler(event,$(this));
			});
		},
		add_scent_handler: function(event, $el){
			if(this.remaining_scents <= 0){
				if($el.is(':visible')){
					$el.toggle();
				}
			}else{
				var new_scent_html = QWeb.render('new_scent', {widget:this})
				var $new_scent_html = $(new_scent_html)
				if($new_scent_html.is(':hidden')){
					$new_scent_html.toggle();
				}
				$new_scent_html.insertBefore($el.parent().parent());

				var $new_scent_hidden = $('tr.new_scent:hidden');
				if ($new_scent_hidden){
					$new_scent_hidden.toggle();
				}

				var scent_id_visible = $('#scent_id:visible')
				if (scent_id_visible){
					var product_scents = this.pos.db.get_product_scent();
					var scents = []
					_.forEach(product_scents, function(product){
						scents.push({
							id: product.id,
							text: product.display_name
						})
					})
					$('#scent_id:visible').select2({
						width: '100%',
						allowClear: true,
						multiple: true,
						maximumSelectionSize: 1,
						placeholder: "Type Scent",
						data: scents
					});
				}
				this.remaining_scents-=1
			}
		},
		onchange_scent_handler: function(event,$el){
			console.log($el);
		},
		remove_scent_handler: function(event, $el){
			this.remaining_scents+=1
			$el.remove()
			if(this.remaining_scents > 0 && $('#add_scent').is(':hidden')){
				$('#add_scent').toggle();
			}
		},
    });


	gui.define_popup({name:'pos_perfume_configurator', widget: PerfumeConfigWidget});

	// var PerfumeConfigButton = screens.ActionButtonWidget.extend({
	//     template: 'ParfumeConfigButton',
    //     events: {
    //         'click .button.back':  'click_back',
    //     },
	//     button_click: function(){
	//         var product  = this.pos.db.get_product_by_id(this.pos.config.wildcard_product_id[0]);
	//         this.gui.show_popup('pos_perfume_configurator');
	//     },
	// });


	// screens.define_action_button({
	//     'name': 'perfumeconfigurator',
	//     'widget': PerfumeConfigButton
	// });

});