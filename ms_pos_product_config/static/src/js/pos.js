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

			// get indexof bottle
			var idx = order.orderlines.indexOf(this.bottle_order_line);

			// value checking
			var valid = true;
			// section name checking
			if(!section_name || section_name == ""){
				self.do_notify('error',_t('Engrave Name Is Required'));
				$('input.section_name').css('border', '1px solid red');
				valid = false
			}else{
				$(this).css('border', 'none');

			}
			// scent schecking
			$('input[name^="scent"]').map(function(){
				var value = $(this).val()
				if($(this).hasClass('scent_id')){
					scent_id = parseInt(value)
					if(!value || value == ""){
						self.do_notify('error',_t('A Scent Is Required'));
						$(this).siblings('.select2-container').css('border', '1px solid red');
						valid = false
					}else{
						$(this).siblings('.select2-container').css('border', 'none');

					}
				}
				if($(this).hasClass('scent_qty')){
					var scent_qty = parseFloat(value)
					if(!value || value == ""){
						self.do_notify('error',_t('A Scent Qty Is Required'));
						$(this).css('border', '1px solid red');
						valid = false
					}else{
						$(this).css('border', 'none');

					}
				}
			}).get();

			if (!valid){
				return false
			}

			var scent_id;
			$('input[name^="scent"]').map(function(){
				var value = $(this).val()
				if($(this).hasClass('scent_id')){
					scent_id = parseInt(value)
				}
				if($(this).hasClass('scent_qty')){
					var scent_qty = parseFloat(value)
					var product = self.pos.db.get_product_by_id(scent_id);
					var scent_line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
					scent_line.set_quantity(scent_qty);
					scent_line.set_unit_price(product.get_price(order.pricelist, scent_qty));
					self.bottle_order_line.scent_lines.push(scent_line)
					order.orderlines.add(scent_line, {at: idx});
					idx+=1;
					self.bottle_order_line.remaining_scents -= 1;
				}
			}).get();

	        var section_line = new models.Orderline({}, {pos: this.pos, order: order, product: product});
	        section_line.set_quantity(0);
            section_line.set_unit_price(0);
            section_line.set_is_section_product(true);
            section_line.set_section_name(section_name);

			// add section name before bottle
			order.orderlines.add(section_line, {at: idx})
			this.bottle_order_line.engrave_line = section_line

			this.gui.close_popup();
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
				if(this.remaining_scents <= 1){
					if($el.is(':visible')){
						$el.toggle();
					}
				}
				var new_scent_html = QWeb.render('new_scent', {widget:this})
				var node = document.createElement('tr');
				node.className = 'new_scent'
				var el_node = _.str.trim(new_scent_html);
				node.innerHTML = el_node
				var delete_button = node.querySelector('button.delete_scent');
				delete_button.addEventListener('click', (function(ev) {
                    this.remove_scent_handler(ev, $(ev.currentTarget))
                }.bind(this)));
				$(node).insertBefore($el.parent().parent());

				var $new_scent_hidden = $('tr.new_scent:hidden');
				if ($new_scent_hidden){
					$new_scent_hidden.toggle();
				}

				var scent_id_visible = $('input.scent_id:visible')
				if (scent_id_visible){
					var product_scents = this.pos.db.product_scents;
					var scents = []
					_.forEach(product_scents, function(product){
						scents.push({
							id: product.id,
							text: product.display_name
						})
					})
					$('input.scent_id:visible').select2({
						width: '100%',
						allowClear: true,
						multiple: false,
						// maximumSelectionSize: 1,
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
			$el.parent().parent().remove()
			this.remaining_scents += 1;
			if(this.remaining_scents > 0 && $('a#add_scent').is(':hidden')){
				$('a#add_scent').toggle();
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