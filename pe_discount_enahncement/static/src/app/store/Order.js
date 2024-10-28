/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(Order.prototype, {
	async _activateCode(code) {
        const rule = this.pos.rules.find((rule) => {
            return rule.mode === "with_code" && (rule.promo_barcode === code || rule.code === code);
        });
        let claimableRewards = null;
        let coupon = null;
        if (rule) {
            if (
                rule.program_id.date_from &&
                this.date_order < rule.program_id.date_from.startOf("day")
            ) {
                return _t("That promo code program is not yet valid.");
            }
            if (rule.program_id.date_to && this.date_order > rule.program_id.date_to.endOf("day")) {
                return _t("That promo code program is expired.");
            }
            const program_pricelists = rule.program_id.pricelist_ids;
            if (
                program_pricelists.length > 0 &&
                (!this.pricelist || !program_pricelists.includes(this.pricelist.id))
            ) {
                return _t("That promo code program requires a specific pricelist.");
            }
            // if (this.codeActivatedProgramRules.includes(rule.id)) {
            //     return _t("That promo code program has already been activated.");
            // }
            this.codeActivatedProgramRules.push(rule.id);
            await this._updateLoyaltyPrograms();
            claimableRewards = this.getClaimableRewards(false, rule.program_id.id);
        } else {
            if (this.codeActivatedCoupons.find((coupon) => coupon.code === code)) {
                return _t("That coupon code has already been scanned and activated.");
            }
            const customerId = this.get_partner() ? this.get_partner().id : false;
            const { successful, payload } = await this.env.services.orm.call(
                "pos.config",
                "use_coupon_code",
                [
                    [this.pos.config.id],
                    code,
                    this.date_order,
                    customerId,
                    this.pricelist ? this.pricelist.id : false,
                ]
            );
            if (successful) {
                // Allow rejecting a gift card that is not yet paid.
                const program = this.pos.program_by_id[payload.program_id];
                if (program && program.program_type === "gift_card" && !payload.has_source_order) {
                    const { confirmed } = await this.env.services.popup.add(ConfirmPopup, {
                        title: _t("Unpaid gift card"),
                        body: _t(
                            "This gift card is not linked to any order. Do you really want to apply its reward?"
                        ),
                    });
                    if (!confirmed) {
                        return _t("Unpaid gift card rejected.");
                    }
                }
                coupon = new PosLoyaltyCard(
                    code,
                    payload.coupon_id,
                    payload.program_id,
                    payload.partner_id,
                    payload.points,
                    payload.expiration_date
                );
                this.pos.couponCache[coupon.id] = coupon;
                this.codeActivatedCoupons.push(coupon);
                await this._updateLoyaltyPrograms();
                claimableRewards = this.getClaimableRewards(coupon.id);
            } else {
                return payload.error_message;
            }
        }
        if (claimableRewards && claimableRewards.length === 1) {
            if (
                claimableRewards[0].reward.reward_type !== "product" ||
                !claimableRewards[0].reward.multi_product
            ) {
                this._applyReward(claimableRewards[0].reward, claimableRewards[0].coupon_id);
                this._updateRewards();
            }
        }
        if (!rule && this.orderlines.length === 0 && coupon) {
            return _t(
                "Gift Card: %s\nBalance: %s",
                code,
                this.env.utils.formatCurrency(coupon.balance)
            );
        }
        return true;
    },
});