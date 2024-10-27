/* @odoo-modules */

import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    /**
     * Checks if the current line applies for a global discount from `pos_discount.DiscountButton`.
     * @returns Boolean
     */

    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.name = this.name || "";
        // this.is_division = this.is_division || false;
        this.display_type = this.display_type || false;
    },
    
    set_is_section_product(){
		this.display_type = 'line_section'
	},

	get_is_section_product(){
		return this.display_type;
	},
	set_section_name(name){
    	this.name = name;
    },
    get_section_name(){
    	return this.name;
    },
    export_for_printing(){
        var lines = super.export_for_printing(...arguments);
        lines.product = this.product;
        lines.name = this.get_section_name() || '';
        return lines;
    },
    export_as_JSON() {
        var self = this;
        var lines =super.export_as_JSON(...arguments);
        lines.name = this.get_section_name() || '';
        lines.display_type = this.get_is_section_product() || false;
        return lines
    },
    init_from_JSON(json) {
    	super.init_from_JSON(...arguments); 
        this.name = json.name;
        this.display_type = this.display_type;
    },

    get_product_id(){
        return this.get_product().id;
    },
    getDisplayData() {
        return {
           ...super.getDisplayData(),
            name: this.get_section_name(),
            id: this.get_product_id(),
        };
    },

});