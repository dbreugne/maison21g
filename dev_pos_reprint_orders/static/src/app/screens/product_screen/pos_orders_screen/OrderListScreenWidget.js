/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { debounce } from "@web/core/utils/timing";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useRef, useState } from "@odoo/owl";
import { OrderlistLine } from "@dev_pos_reprint_orders/app/screens/product_screen/pos_orders_screen/pos_orders_line";


export class OrderListScreenWidget extends Component {
    static components = { OrderlistLine };
    static template = "dev_pos_reprint_orders.OrderListScreenWidget";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        
        this.state = useState({
            query: null,
            selectedPosOrder: this.props.partner,
        });
        this.orders = this.get_pos_orders()[0] || [];
        this.orderlines = this.get_pos_orders()[1] || [];
        this.searchWordInputRef = useRef('search-word-input-pos-order');
        this.syncOrderList = debounce(this.syncOrderList, 70);
    }

    back() {
        this.pos.closeTempScreen();
        this.pos.showScreen("ProductScreen");
    }

    syncOrderList(event) {
        this.state.query = event.target.value;
        const pos_orders = this.pos_orders;
        if (event.code === 'Enter' && pos_orders.length === 1) {
            this.state.selectedPosOrder = pos_orders[0];
        } else {
            this.render();
        }
    }

    async _clearSearch() {
        this.searchWordInputRef.el.value = "";
        this.state.query = "";
        this.render(true);
    }

    get_last_day_domain_date() {

        var date = new Date();
        var last = new Date(date.getTime() - this.pos.config.last_days * 24 * 60 * 60 * 1000);
              
        let dd = last.getDate();
        let mm = last.getMonth()+1; //January is 0!
        let yyyy = last.getFullYear();
        if(dd<10){
            dd='0'+dd;
        } 
        if(mm<10){
            mm='0'+mm;
        } 
        last = yyyy+'-'+mm+'-'+dd;
        return last;
    }

    get_orders_domain(){
        let self = this; 
        let current = self.pos.pos_session.id;
        let pos_config = self.pos.config;
        let last_day_date = self.get_last_day_domain_date();
        return [['state','not in',['cancel']],['date_order', '>=', last_day_date + ' 00:00:00']];
    }

    async get_pos_orders () {
        let self = this;
        let domain = self.get_orders_domain();
        var fields = ['name','pos_reference','partner_id','session_id','amount_total','date_order','lines','payment_ids'];
        let load_orders = [];
        let load_orders_line = [];
        let order_list = [];
        try {
            await this.orm.call(
                "pos.order",
                "search_read",
                [],
                {domain,fields},
                ).then(function(output) {

                    load_orders = output;
                    self.pos.db.get_orders_by_id = {};
                    self.pos.db.get_orders_by_barcode = {};
                    load_orders.forEach(function(order) {
                        order_list.push(order.id)
                        self.pos.db.get_orders_by_id[order.id] = order;     
                        self.pos.db.get_orders_by_barcode[order.barcode] = order;                       
                    });

                    self.orm.call(
                        "pos.order.line",
                        "search_read",
                        [[['order_id','in',order_list]]],
                        ).then(function(output1) {
                            self.pos.db.all_orders_line_list = output1;
                            load_orders_line = output1;

                            self.pos.synch.all_orders_list = load_orders
                            self.pos.synch.all_orders_line_list = output1

                            self.orders = load_orders;
                            self.orderlines = output1;

                            self.pos.db.get_orderline_by_id = {};
                            output1.forEach(function(ol) {
                                self.pos.db.get_orderline_by_id[ol.id] = ol;                        
                            });

                            self.render();
                            return [load_orders,load_orders_line]
                        }
                    )                    
                }
            ); 
        }catch (error) {
            if (error.message.code < 0) {
                await this.popup.add('OfflineErrorPopup', {
                    title: _t('Offline'),
                    body: _t('Unable to load orders.'),
                });
            } else {
                throw error;
            }
        }
    }

    get pos_orders() {
        let self = this;
        let query = this.state.query;
        if(query){
            query = query.trim();
            query = query.toLowerCase();
        }
        if(this.orders){
            if ((query && query !== '') || 
                (this.props.select_order_id)) {
                return this.search_order(this.orders,query);
            } else {
                return this.orders;
            }
        }
        else{
            let odrs = this.get_pos_orders()[0] || [];
            if (query && query !== '') {
                return this.search_order(odrs,query);
            } else {
                return odrs;
            }
        }
    }

    search_order(orders,query){
        var self = this;
        let searched_order = [];
        
        let search_order = query;
        orders.forEach(function(odr) {
            if ((odr.partner_id == '' || !odr.partner_id) && search_order) {
                if (((odr.name.toLowerCase()).indexOf(search_order) != -1) || 
                    ((odr.date_order).indexOf(search_order) != -1)||
                    ((odr.pos_reference.toLowerCase()).indexOf(search_order) != -1)) {
                    searched_order.push(odr);
                }
            }
            else
            {
                if(search_order){
                    if (((odr.name.toLowerCase()).indexOf(search_order) != -1) || 
                        ((odr.date_order).indexOf(search_order) != -1)||
                        ((odr.pos_reference.toLowerCase()).indexOf(search_order) != -1)|| 
                        ((odr.partner_id[1].toLowerCase()).indexOf(search_order) != -1)) {
                        searched_order.push(odr);
                    }
                }
            }
        });
        if (searched_order.length > 0){
            return searched_order;
        }else{
            searched_order = [];
            return searched_order;
        }
    }

    async clickReprint(order){
        let self = this;
        await this.orm.call(
            "pos.order",
            "pos_order_reprint_data",
            [[order.id]],
            ).then(function(output) {
                let data = output;
                data['order'] = order;
                self.pos.showScreen('OrderReprintScreen',data);
            }
        );
    }
}

registry.category("pos_screens").add("OrderListScreenWidget", OrderListScreenWidget);