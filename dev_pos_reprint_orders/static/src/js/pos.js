odoo.define('dev_pos_reprint_order.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var DB = require('point_of_sale.DB');
    var QWeb = core.qweb;
    var _t = core._t;

    models.PosModel.prototype.models.push({
        model:  'pos.order',
        fields: ['name','pos_reference','partner_id','session_id','amount_total','date_order','lines','payment_ids'],
        domain: function(self) {return [['session_id', '=', self.pos_session.id]]},
        loaded: function(self,orders){
            self.pos_orders = orders;
            self.db.add_pos_orders(orders);
        },
    });

    var _super_Order = models.Order.prototype;
	models.Order = models.Order.extend({
		set_journal: function(statement_ids) {
            this.set('statement_ids', statement_ids)
        },
        get_journal: function() {
            return this.get('statement_ids');
        },
        set_reprint_change: function(reprint_change) {
            this.set('reprint_change', reprint_change)
        },
        get_reprint_change: function() {
            return this.get('reprint_change');
        },
        set_reprint_order_ref: function(reprint_order_ref) {
            this.set('reprint_order_ref', reprint_order_ref)
        },
        get_reprint_order_ref: function() {
            return this.get('reprint_order_ref');
        },
		export_for_printing: function(){
            var orders = _super_Order.export_for_printing.call(this);
            orders['reprint_payment'] = this.get_journal() || false;
            orders['reprint_change'] = this.get_reprint_change() || false;
            orders['reprint_order_name'] = this.get_reprint_order_ref() || false; 
            return orders;
        },
	});

    var ShowOrdersButtonWidget = screens.ActionButtonWidget.extend({
        template: 'ShowOrdersButtonWidget',
        button_click: function(){
            var self = this;
        	self.gui.show_screen('orderlist');
        },
    });
    screens.define_action_button({
        'name': 'show_pos_orders',
        'widget': ShowOrdersButtonWidget,
        'condition': function(){
            return this.pos.config.load_pos_order;
        },
    });

    var OrderListScreenWidget = screens.ScreenWidget.extend({
	    template: 'OrderListScreenWidget',
	    events: {
	    	'click .button.back':  'click_back',
	    	'keyup .searchbox input': 'search_order',
	    	'click .searchbox .search-clear': 'clear_search',
	    	'click #print_order': 'click_reprint',
	    },
	    init: function(parent, options){
	    	var self = this;
	        this._super(parent, options);
	        if(this.pos.config.iface_vkeyboard && self.chrome.widget.keyboard){
            	self.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
	    },
	    clear_cart: function(){
        	var self = this;
        	var order = self.pos.get_order();
            var currentOrderLines = order.get_orderlines();
            var lines_ids = []
         	if(!order.is_empty()) {
         		_.each(currentOrderLines,function(item) {
         			lines_ids.push(item.id);
         		});
		        _.each(lines_ids,function(id) {
		        	order.remove_orderline(order.get_orderline(id));
		        });
         	}
        },
	    click_reprint: function(event){
        	var self = this;
        	var selectedOrder = this.pos.get_order();
        	var order_id = parseInt($(event.currentTarget).data('id'));
        	self.clear_cart();
        	selectedOrder.set_client(null);
        	var result = self.pos.db.get_order_by_id(order_id);
        	if (result && result.lines.length > 0) {
        		if (result.partner_id && result.partner_id[0]) {
                    var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    if(partner){
                    	selectedOrder.set_client(partner);
                    }
                }
                selectedOrder.set_reprint_order_ref(result.pos_reference);
                if(result.payment_ids){
                    if(result.payment_ids.length > 0){
                        self.get_journal_from_order(result.payment_ids);
                    }
                }
                if(result.lines.length > 0){
                    self.get_orderlines_from_order(result.lines).then(function(){
                        var order_lines = self.pos.get('orderlines');
                        if(order_lines.length > 0){
                            _.each(order_lines, function(line){
                                var product = self.pos.db.get_product_by_id(Number(line.product_id[0]));
                                if(product){
                                    selectedOrder.add_product(product, {
                                        quantity: line.qty,
                                        discount: line.discount,
                                        price: line.price_unit,
                                    })
                                }
                            })
                        }
						self.gui.show_screen('receipt')
                    });
                }
        	}
        },
        get_journal_from_order: function(statement_ids){
	    	var self = this;
	    	var order = this.pos.get_order();
	    	var params = {
	    		model: 'pos.payment',
	    		method: 'search_read',
	    		domain: [['id', 'in', statement_ids]],
                fields: self.fieldNames,
	    	}
	    	rpc.query(params, {async: false}).then(function(statements){
	    		if(statements.length > 0){
	    			var order_statements = []
	    			_.each(statements, function(statement){
	    				if(statement.amount > 0){
	    					order_statements.push({
	    						amount: statement.amount,
	    						journal: statement.payment_method_id[1],
	    					})
	    				} else{
	    					var change = order.get_reprint_change() || 0
	    					change += statement.amount
	    					order.set_reprint_change(change)
	    				}
	    			});
	    			order.set_journal(order_statements);
	    		}
	    	});
	    },
	    get_orderlines_from_order: function(line_ids){
	    	var self = this;
	    	var order = this.pos.get_order();
	    	var orderlines = false;
	    	var line_id = [];
            return new Promise(function (resolve, reject) {
                var params = {
                    model: 'pos.order.line',
                    method: 'search_read',
                    domain: [['id', 'in', line_ids]],
                    fields: self.fieldNames,
                }
                rpc.query(params, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function (order_lines) {
                    if(order_lines){
                        if(order_lines.length > 0){
                            orderlines = order_lines;
                        }
                        self.pos.set({'orderlines':orderlines})
                        resolve();
                    }else {
                        reject();
                    }
                }, function (type, err) { reject(); });
            });

	    },
	    click_back: function(){
        	this.gui.show_screen('products');
        },
        show: function(){
	        this._super();
	        this.render_list(this.pos.pos_orders || []);
	    },
	    search_order: function(event){
	    	var self = this;
	    	var search_timeout = null;
	    	clearTimeout(search_timeout);
            var query = $(event.currentTarget).val();
            search_timeout = setTimeout(function(){
                self.perform_search(query,event.which === 13);
            },70);
	    },
	    perform_search: function(query, associate_result){
	    	var self = this;
            if(query){
                var orders = this.pos.db.search_order(query);
                if ( associate_result && orders.length === 1){
                    this.gui.back();
                }
                this.render_list(orders);
            }else{
                var orders = self.pos.pos_orders;
                this.render_list(orders);
            }
        },
        clear_search: function(){
            var orders = this.pos.pos_orders;
            this.render_list(orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        render_list: function(orders){
        	var self = this;
        	if(orders){
	            var contents = this.$el[0].querySelector('.order-list-contents');
	            contents.innerHTML = "";
	            var temp = [];
	            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
	                var order = orders[i];
	                order.amount_total = parseFloat(order.amount_total).toFixed(2);
	            	var clientline_html = QWeb.render('OrderlistLine',{widget: this, order:order});
	                var clientline = document.createElement('tbody');
	                clientline.innerHTML = clientline_html;
	                clientline = clientline.childNodes[1];
	                contents.appendChild(clientline);
	            }
        	}
        },
    });
    gui.define_screen({name:'orderlist', widget: OrderListScreenWidget});

    var _super_posmodel = models.PosModel;
	models.PosModel = models.PosModel.extend({
		_save_to_server: function (orders, options) {
			var self = this;
			return _super_posmodel.prototype._save_to_server.apply(this, arguments)
			.then(function(server_ids){
				var server_list_ids = [];
                server_ids.map(function(each_id){
                       server_list_ids.push(each_id.id);
                });
				if(server_list_ids.length > 0 && self.config.load_pos_order){
					var params = {
						model: 'pos.order',
						method: 'search_read',
						domain:[['id','in',server_list_ids],['session_id', '=',self.pos_session.id]],
					}
					rpc.query(params, {async: false}).then(function(orders){
		                if(orders.length > 0){
		                	orders = orders[0];
		                    var exist_order = _.findWhere(self.pos_orders, {'pos_reference': orders.pos_reference})
		                    if(exist_order){
		                    	_.extend(exist_order, orders);
		                    } else {
		                    	self.pos_orders.push(orders);
		                    }
		                    var new_orders = _.sortBy(self.pos_orders, 'id').reverse();
		                    self.db.add_pos_orders(new_orders);
		                    self.pos_orders = new_orders;
		                }
		            });
				}
			});
		}, 
	});

    DB.include({
		init: function(options){
			this._super.apply(this, arguments);
			this.order_write_date = null;
        	this.order_by_id = {};
        	this.line_by_id = {};
        	this.order_sorted = [];
        	this.order_search_string = "";
		},
		add_pos_orders: function(orders){
            var updated_count = 0;
            var new_write_date = '';
            for(var i = 0, len = orders.length; i < len; i++){
                var order = orders[i];
                if (    this.order_write_date && 
                        this.order_by_id[order.id] &&
                        new Date(this.order_write_date).getTime() + 1000 >=
                        new Date(order.write_date).getTime() ) {
                    continue;
                } else if ( new_write_date < order.write_date ) { 
                    new_write_date  = order.write_date;
                }
                if (!this.order_by_id[order.id]) {
                    this.order_sorted.push(order.id);
                }
                this.order_by_id[order.id] = order;
                updated_count += 1;
            }
            this.order_write_date = new_write_date || this.order_write_date;
            if (updated_count) {
                // If there were updates, we need to completely 
                this.order_search_string = "";
                for (var id in this.order_by_id) {
                    var order = this.order_by_id[id];
                    this.order_search_string += this._order_search_string(order);
                }
            }
            return updated_count;
        },
        _order_search_string: function(order){
            var str =  order.name;
            if(order.pos_reference){
                str += '|' + order.pos_reference;
            }
            if(order.partner_id.length > 0){
                str += '|' + order.partner_id[1];
            }
            str = '' + order.id + ':' + str.replace(':','') + '\n';
            return str;
        },
        get_order_write_date: function(){
            return this.order_write_date;
        },
        get_order_by_id: function(id){
            return this.order_by_id[id];
        },
        search_order: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(' ','.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            var r;
            for(var i = 0; i < this.limit; i++){
                r = re.exec(this.order_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_order_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        },
    });
});
