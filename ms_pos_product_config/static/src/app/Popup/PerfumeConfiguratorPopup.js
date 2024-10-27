/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState, onMounted } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Orderline } from "@point_of_sale/app/store/models";


export class PerfumeConfigWidget extends AbstractAwaitablePopup {
    static template = "ms_pos_product_config.ParfumeConfigWIdget";
    static defaultProps = { confirmKey: false };

    setup() {
        super.setup();
        this.pos = usePos();
        this.remaining_scents = this.props.remaining_scents;
        this.bottle_order_line = this.props.bottle_order_line || false;
        this.section_order_line = this.props.section_order_line || false;
        this.scent_order_lines = this.props.scent_order_lines || [];
        this.selected_scents = this.props.selected_scents || [];
        this.bottle_name = this.props.bottle_name || '';
        this.section_name = this.props.section_name || '';

        this.product_scents = {};
        onMounted(this.onMounted);
        Object.assign(this, this.props.info);
    }

    onMounted() {
        $("#select_scent_container").hide()
    }

    addScentHandler() {
        $("#add_scent_container").hide()
        $("#select_scent_container").show()

        this.remaining_scents-=1
        
    }

    deleteScent(){
        this.remaining_scents += 1;

        if(this.remaining_scents > 0 && $("#add_scent_container").hide()){
            $("#add_scent_container").show()
            $("#select_scent_container").hide()
        }
    }


    async confirm() {

        var self = this
        var section_name = $('input.section_name').val();
        var id = self.pos.config.wildcard_product_id[0];
        var wildcard_product = self.pos.db.get_product_by_id(id);
        if (!wildcard_product){
            alert("Section product is not configured")
            return false
        }
        var order = self.pos.get_order();

        // adding bottle_line_id
        // get indexof bottle
        var idx = order.orderlines.indexOf(this.bottle_order_line);
        var bottle_line_idx = idx;
        idx+=1;


        // value checking
        var valid = true;
        // section name checking
        if(!section_name || section_name == ""){
            alert("Engrave Name Is Required")
            $('input.section_name').css('border', '1px solid red');
            valid = false
        }else{
            $('input.section_name').css('border', 'none');
        }

        var scent_prod_id = false
        if ($("#select_scent_container").is(":visible")){

            scent_prod_id = $('#scent_id').find(":selected").val();
            if (!scent_prod_id){
                alert("A Scent Is Required")
                $('#scent_id').css('border', '1px solid red');
                valid = false
                return false
            }else{
                $('#scent_id').css('border', 'none');
            }

            var scent_qty = $('#scent_qty').val();
            if (!scent_qty){
                alert("A Scent Qty Is Required")
                $('#scent_qty').css('border', '1px solid red');
                valid = false
            }else{
                $('#scent_qty').css('border', 'none');
            }
        }

        if (!valid){
            return false
        }

        if (scent_prod_id){
            var product = self.pos.db.get_product_by_id(scent_prod_id);
            // nambah order line
            var scent_line = new Orderline(
                { env: this.env },
                {
                    pos: this.pos,
                    order: order,
                    product: product,
                }
            );

            scent_line.set_quantity(scent_qty);
            scent_line.set_unit_price(product.get_price(order.pricelist, scent_qty));
            scent_line.bottle_line_idx = bottle_line_idx;
            self.bottle_order_line.scent_lines.push(scent_line)
            order.orderlines.add(scent_line, {at: idx});
            idx+=1;
            self.bottle_order_line.remaining_scents -= 1;
        }

        var section_line = new Orderline(
            { env: this.env },
            {
                pos: this.pos,
                order: order,
                product: wildcard_product,
            }
        );
        // var section_line = new models.Orderline({}, {pos: this.pos, order: order, product: product});
        section_line.set_quantity(0);
        section_line.set_unit_price(0);
        section_line.set_is_section_product(true);
        section_line.set_section_name(section_name);

        // add section name after bottle
        idx+=1;
        order.orderlines.add(section_line, {at: idx})
        this.bottle_order_line.engrave_line = section_line

        self.props.close({ confirmed: true});
    }

    cancel(){
        var order = this.pos.get_order()

        if (order){
            var selected_line = order.get_selected_orderline()
            if (selected_line){
                order.removeOrderline(selected_line)
            }
        }

        this.props.close({ confirmed: false, payload: null });
    }
    
}
