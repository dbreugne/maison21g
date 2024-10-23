/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { WildCardPopup } from "@dev_pos_line_section/js/WildCardPopup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { parseFloat } from "@web/views/fields/parsers";

export class SectionButton extends Component {
    static template = "dev_pos_line_section.SectionButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async click() {
        var self = this;
        const { confirmed, payload } = await this.popup.add(WildCardPopup, {
            title: _t("Add Section"),
        });

        var product  = this.pos.db.get_product_by_id(this.pos.config.wildcard_product_id[0]);
        if (!product) {
            return alert(_t("No section product found"));
        }
    }
}

ProductScreen.addControlButton({
    component: SectionButton,
    condition: function () {
        return this.pos.config.iface_widcard && this.pos.config.wildcard_product_id;
    },
});