/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { Orderline } from "@point_of_sale/app/store/models";

export class WildCardPopup extends AbstractAwaitablePopup {
	static template = "dev_pos_line_section.WildCardPopup";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
    }

    async confirm() {
        let self  = this;
        var product_name = $("#product_name").val();
        if(product_name == 'undefined'){
        	return alert(_t("Enter Section Name"));
        }
        var id = self.pos.config.wildcard_product_id[0];
        var product = self.pos.db.get_product_by_id(id);
        var order = self.pos.get_order();
        var line = new Orderline(
            { env: this.env },
            {
                pos: this.pos,
                order: order,
                product: product,
            }
        );

        line.set_quantity(0);
        line.set_unit_price(0);
        line.set_is_section_product(true);
        line.set_section_name(product_name);
        order.add_orderline(line);

		self.props.close({ confirmed: true});
    }
}