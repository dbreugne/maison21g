/** @odoo-module */

import { PosDB } from "@point_of_sale/app/store/db";
import { unaccent } from "@web/core/utils/strings";
import { patch } from "@web/core/utils/patch";

patch(PosDB.prototype, {
    constructor(options) {
		this.order_write_date = null;
    	this.order_by_id = {};
    	this.line_by_id = {};
    	this.order_sorted = [];
    	this.order_search_string = "";
	},
});
