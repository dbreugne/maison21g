/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class ShowOrdersButtonWidget extends Component {
    static template = "dev_pos_reprint_orders.ShowOrdersButtonWidget";

    setup() {
        this.pos = usePos();
    }
    
    click() {
        this.pos.showScreen('OrderListScreenWidget', {
            'select_order_id': false,
        });
    }
}

ProductScreen.addControlButton({
    component: ShowOrdersButtonWidget,
    condition: function () {
        return this.pos.config.load_pos_order;
    },
});
