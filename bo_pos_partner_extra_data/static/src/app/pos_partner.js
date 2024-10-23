/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";

patch(PartnerDetailsEdit.prototype, {
    setup() {
        const res = super.setup(...arguments);
        this.changes.birthdate = this.props.partner.birthdate;
        this.changes.married = this.props.partner.married;
        this.changes.gender = this.props.partner.gender;
        this.changes.children = this.props.partner.children;
        this.changes.date_wedding = this.props.partner.date_wedding;
        this.changes.no_children = this.props.partner.no_children;


        this.married_data = [{'code': 'yes', 'name': _t('Yes')}, {'code': 'no', 'name': _t('No')}];
        this.genders_data = [{'code': 'female', 'name': _t('Female')},{'code': 'male', 'name': _t('Male')},{'code': 'unisex', 'name': _t('Unisex')}];
        this.children =[{'code': 'yes', 'name': _t('Yes')}, {'code': 'no', 'name': _t('No')}];
        return res;
    },
    
});