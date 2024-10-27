/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { PosDB } from "@point_of_sale/app/store/db";
import { unaccent } from "@web/core/utils/strings";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PerfumeConfigWidget } from "@ms_pos_product_config/app/Popup/PerfumeConfiguratorPopup";

patch(PosStore.prototype, {
    // @Override
    async addProductToCurrentOrder(product, options = {}) {
        if (Number.isInteger(product)) {
            product = this.db.get_product_by_id(product);
        }
        this.get_order() || this.add_new_order();

        options = { ...(await product.getAddProductOptions()), ...options };

        if (!Object.keys(options).length) {
            return;
        }

        // Add the product after having the extra information.
        await this.addProductFromUi(product, options);
        this.numberBuffer.reset();

        console.log("product---------------",product)
        if (product.tracking == 'lot' && product.is_bottle !== false) {
            var bottle_order_line_id = this.get_order().get_last_orderline();
            
            this.env.services.popup.add(PerfumeConfigWidget, {
                bottle: product,
                remaining_scents: product.max_number_of_scents,
                bottle_name: product.display_name,
                selected_scents: [],
                bottle_order_line: bottle_order_line_id,
            });
        }
    },

    async _processData(loadedData) {
        this.db.product_scents = [];
        super._processData(...arguments);
    }
});

patch(PosDB.prototype, {
    
    add_products(products) {
        var stored_categories = this.product_by_category_id;

        if (!(products instanceof Array)) {
            products = [products];
        }
        for (var i = 0, len = products.length; i < len; i++) {
            var product = products[i];
            if (product.id in this.product_by_id) {
                continue;
            }
            if (product.available_in_pos) {
                var search_string = unaccent(this._product_search_string(product));
                const all_categ_ids = product.pos_categ_ids.length
                    ? product.pos_categ_ids
                    : [this.root_category_id];
                product.product_tmpl_id = product.product_tmpl_id[0];
                for (const categ_id of all_categ_ids) {
                    if (!stored_categories[categ_id]) {
                        stored_categories[categ_id] = [];
                    }
                    stored_categories[categ_id].push(product.id);

                    if (this.category_search_string[categ_id] === undefined) {
                        this.category_search_string[categ_id] = "";
                    }
                    this.category_search_string[categ_id] += search_string;

                    var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                    for (var j = 0, jlen = ancestors.length; j < jlen; j++) {
                        var ancestor = ancestors[j];
                        if (!stored_categories[ancestor]) {
                            stored_categories[ancestor] = [];
                        }
                        stored_categories[ancestor].push(product.id);

                        if (this.category_search_string[ancestor] === undefined) {
                            this.category_search_string[ancestor] = "";
                        }
                        this.category_search_string[ancestor] += search_string;
                    }
                }
            }

            if(product.is_scent){
                this.product_scents.push(product);
            }
            
            this.product_by_id[product.id] = product;
            if (product.barcode && product.active) {
                this.product_by_barcode[product.barcode] = product;
            }
            if (this.product_by_tmpl_id[product.product_tmpl_id]) {
                this.product_by_tmpl_id[product.product_tmpl_id].push(product);
            } else {
                this.product_by_tmpl_id[product.product_tmpl_id] = [product];
            }
        }
    }
});


patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.selected_scent = []
        this.engrave_line = options.engrave_line || false;
        this.scent_lines = options.scent_lines || [];
        this.remaining_scents = options.remaining_scents || 0;
        this.bottle_line_idx = false;
    },

    can_be_merged_with(orderline) {
        var res = super.can_be_merged_with(...arguments);

        var product = this.product;
        if(product && (product.is_bottle || product.scent)){
            return false;
        }

        var product = orderline.product;
        if(product && (product.is_bottle || product.scent)){
            return false;
        }

        return res
    },
    export_as_JSON() {
        var self = this;
        var json =super.export_as_JSON(...arguments);
        json.bottle_line_idx = this.bottle_line_idx;
        return json;
    },
});

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
    },

    can_be_merged_with(orderline) {
        var res = super.can_be_merged_with(...arguments);

        var product = this.product;
        if(product && (product.is_bottle || product.scent)){
            return false;
        }

        var product = orderline.product;
        if(product && (product.is_bottle || product.scent)){
            return false;
        }

        return res
    },

    async add_product(product, options) {
        // for product that is not a bottle
        if (product.is_bottle == false) {
            return super.add_product(...arguments);
        }
        // condition if the product is a bottle and has no lot/serial
        else if (product.is_bottle !== false && product.tracking == 'none') {
            var res = super.add_product(...arguments);
            var bottle_location = this.orderlines.length - 1;
            var bottle_order_line_id = this.orderlines[bottle_location];

            this.env.services.popup.add(PerfumeConfigWidget, {
                bottle: product,
                remaining_scents: product.max_number_of_scents,
                bottle_name: product.display_name,
                selected_scents: [],
                bottle_order_line: bottle_order_line_id,
            });

            return res
        }
        // yang dibawah ini else nya (kalau bottle dan line.has_product_lot)
        else {
            if (
                this.pos.doNotAllowRefundAndSales() &&
                this._isRefundOrder() &&
                (!options.quantity || options.quantity > 0)
            ) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: _t("Refund and Sales not allowed"),
                    body: _t("It is not allowed to mix refunds and sales"),
                });
                return;
            }
            if (this._printed) {
                // when adding product with a barcode while being in receipt screen
                this.pos.removeOrder(this);
                return await this.pos.add_new_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            const quantity = options.quantity ? options.quantity : 1;
            const line = new Orderline(
                { env: this.env },
                { pos: this.pos, order: this, product: product, quantity: quantity }
            );
            this.fix_tax_included_price(line);

            this.set_orderline_options(line, options);
            line.set_full_product_name();
            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if (this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false) {
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline) {
                to_merge_orderline.merge(line);
                this.select_orderline(to_merge_orderline);
            } else {
                this.add_orderline(line);
                this.select_orderline(this.get_last_orderline());
            }

            if (options.draftPackLotLines) {
                this.selected_orderline.setPackLotLines({
                    ...options.draftPackLotLines,
                    setQuantity: options.quantity === undefined,
                });
            }

            if (options.comboLines?.length) {
                await this.addComboLines(line, options);
                // Make sure the combo parent is selected.
                this.select_orderline(line);
            }
            this.hasJustAddedProduct = true;
            clearTimeout(this.productReminderTimeout);
            this.productReminderTimeout = setTimeout(() => {
                this.hasJustAddedProduct = false;
            }, 3000);
            return line;

        }

    },
});