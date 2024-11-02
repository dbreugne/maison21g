/** @odoo-module */

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    async onClickRePrint(order) {
        
        if (!order) {
            return;
        }
        // Need to await to have the result in case of automatic skip screen.
        this.pos.showScreen("ReprintReceiptScreen", { order: order });
    },
});
