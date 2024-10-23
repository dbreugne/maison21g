/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onWillUnmount, useRef, onMounted } from "@odoo/owl";

export class OrderReprintReceipt extends Component {
    static template = "dev_pos_reprint_orders.OrderReprintReceipt";

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    }
}

registry.category("pos_screens").add("OrderReprintReceipt", OrderReprintReceipt);