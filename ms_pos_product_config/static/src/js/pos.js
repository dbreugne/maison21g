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

			// adding bottle_line_id
			// get indexof bottle
			var idx = order.orderlines.indexOf(this.bottle_order_line);
			var bottle_line_idx = idx;
			idx+=1;

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
					if(!value || value == ""){
						self.do_notify('error',_t('A Scent Is Required'));
						$(this).siblings('.select2-container').css('border', '1px solid red');
						valid = false
					}else{
						$(this).siblings('.select2-container').css('border', 'none');

					}
				}
				if($(this).hasClass('scent_qty')){
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
					// nambah order line
					var scent_line = new models.Orderline({}, {
						pos: self.pos,
						order: order,
						product: product,
					});
					scent_line.set_quantity(scent_qty);
					scent_line.set_unit_price(product.get_price(order.pricelist, scent_qty));
					scent_line.bottle_line_idx = bottle_line_idx;
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

			// add section name after bottle
			idx+=1;
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
			$('#add_scent').on('select2:select', function (e) {
				var data = e.params.data;
				console.log(data);
			});
			// $('input[name^="scent"]').change(function(event) {
			// 	self.onchange_scent_handler(event,$(this));
			// });
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
				var input_scent = node.querySelector('input.scent_id');
				input_scent.addEventListener('change', function(ev){
					this.onchange_scent_handler(ev, $(ev.currentTarget));
				}.bind(this));
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
		click_cancel: function(){
			if(this.bottle_order_line){
				var order = this.bottle_order_line.order;
				order.remove_orderline(this.bottle_order_line)
			}
			this.gui.close_popup();
		},
    });


	gui.define_popup({ name: 'pos_perfume_configurator', widget: PerfumeConfigWidget });
	
	// var BottlePackLotLinePopupWidget = PopupWidget.extend({
    //     template: 'BottlePackLotLinePopupWidget',
    //     events: _.extend({}, PopupWidget.prototype.events, {
    //         'click .remove-lot': 'remove_lot',
    //         'keydown': 'add_lot',
    //         'blur .packlot-line-input': 'lose_input_focus'
    //     }),

    //     show: function(options){
    //         this._super(options);
    //         this.focus();
    //     },

    //     click_confirm: function(){
    //         var pack_lot_lines = this.options.pack_lot_lines;
    //         this.$('.packlot-line-input').each(function(index, el){
    //             var cid = $(el).attr('cid'),
    //                 lot_name = $(el).val();
    //             var pack_line = pack_lot_lines.get({cid: cid});
    //             pack_line.set_lot_name(lot_name);
    //         });
    //         pack_lot_lines.remove_empty_model();
    //         pack_lot_lines.set_quantity_by_lot();
    //         this.options.order.save_to_db();
    //         this.options.order_line.trigger('change', this.options.order_line);
    //         this.gui.close_popup();
    //         // tambahi kondisi, kalau this.options.order_line.product itu is_bottle, buka Bottle/scent config                        
    //         if (this.options.order_line.product.is_bottle !== false) {
	// 			var bottle_order_line_id = this.options.order_line;
	// 			var product = bottle_order_line_id.product;
    //             this.pos.gui.show_popup('pos_perfume_configurator', {
    //                 bottle: product,
    //                 remaining_scents: product.max_number_of_scents,
    //                 bottle_name: product.display_name,
    //                 selected_scents: [],
    //                 bottle_order_line: bottle_order_line_id,
    //             });
    //         }
    //     },

    //     add_lot: function(ev) {
    //         if (ev.keyCode === $.ui.keyCode.ENTER && this.options.order_line.product.tracking == 'serial'){
    //             var pack_lot_lines = this.options.pack_lot_lines,
    //                 $input = $(ev.target),
    //                 cid = $input.attr('cid'),
    //                 lot_name = $input.val();

    //             var lot_model = pack_lot_lines.get({cid: cid});
    //             lot_model.set_lot_name(lot_name);  // First set current model then add new one
    //             if(!pack_lot_lines.get_empty_model()){
    //                 var new_lot_model = lot_model.add();
    //                 this.focus_model = new_lot_model;
    //             }
    //             pack_lot_lines.set_quantity_by_lot();
    //             this.renderElement();
    //             this.focus();
    //         }
    //     },

    //     remove_lot: function(ev){
    //         var pack_lot_lines = this.options.pack_lot_lines,
    //             $input = $(ev.target).prev(),
    //             cid = $input.attr('cid');
    //         var lot_model = pack_lot_lines.get({cid: cid});
    //         lot_model.remove();
    //         pack_lot_lines.set_quantity_by_lot();
    //         this.renderElement();
    //     },

    //     lose_input_focus: function(ev){
    //         var $input = $(ev.target),
    //             cid = $input.attr('cid');
    //         var lot_model = this.options.pack_lot_lines.get({cid: cid});
    //         lot_model.set_lot_name($input.val());
    //     },

    //     focus: function(){
    //         this.$("input[autofocus]").focus();
    //         this.focus_model = false;   // after focus clear focus_model on widget
    //     }
    // });
    // gui.define_popup({name:'bottlepacklotline', widget:BottlePackLotLinePopupWidget});

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