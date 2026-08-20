/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { Order } from "@point_of_sale/app/store/models";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(Order.prototype, {

    get_total_with_tax() {
        let total_with_tax =  super.get_total_with_tax(...arguments);
        let sign = Math.sign(total_with_tax);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                total_with_tax = sign * (Math.ceil(Math.abs(total_with_tax) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                total_with_tax = sign * (Math.floor(Math.abs(total_with_tax) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                total_with_tax = round_pr(total_with_tax, round_factor);
            }
        }
        return total_with_tax;
    },

    get_total_without_tax() {
        let total_without_tax =  super.get_total_without_tax(...arguments);
        let sign = Math.sign(total_without_tax);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                total_without_tax = sign * (Math.ceil(Math.abs(total_without_tax) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                total_without_tax = sign * (Math.floor(Math.abs(total_without_tax) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                total_without_tax = round_pr(total_without_tax, round_factor);
            }
        }
        return total_without_tax
    },

    get_total_discount () {
        let total_discount =  super.get_total_discount(...arguments);
        let sign = Math.sign(total_discount);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                total_discount = sign * (Math.ceil(Math.abs(total_discount) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                total_discount = sign * (Math.floor(Math.abs(total_discount) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                total_discount = round_pr(total_discount, round_factor);
            }
        }
        return total_discount
    },

    get_total_tax () {
        let total_tax = super.get_total_tax(...arguments);
        let sign = Math.sign(total_tax);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                total_tax = sign * (Math.ceil(Math.abs(total_tax) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                total_tax = sign * (Math.floor(Math.abs(total_tax) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                total_tax = round_pr(total_tax, round_factor);
            }
        }
        return total_tax
    },

    get_total_paid () {
        let total_paid = super.get_total_paid(...arguments);
        let sign = Math.sign(total_paid);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                total_paid = sign * (Math.ceil(Math.abs(total_paid) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                total_paid = sign * (Math.floor(Math.abs(total_paid) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                total_paid = round_pr(total_paid, round_factor);
            }
        }
        return total_paid
    },

    async pay() {
        if (this.pos.config.rounding_automatic) {
            await this.roundingTotalAmount()
        }
        return super.pay(...arguments);
    },

    async roundingTotalAmount() {
        var self = this;
        let selectedOrder = this.pos.get_order();


        const lines = selectedOrder.get_orderlines();

        for (let line of lines) {
            if (!line.kg || !line.pieces) {
                await this.pos.popup.add(ErrorPopup, {
                    title: _t("Warning"),
                    body: _t("Please check all products have kg and pieces correctly"),
                });
                  break;

            }
        }

        let roundingMethod = this.pos.payment_methods.find((p) => p.journal && p.journal.pos_method_type == 'rounding')
        if (!selectedOrder || !roundingMethod) {
            return this.pos.popup.add(ErrorPopup, {
                title: _t("Warning"),
                body: _t("You active Rounding on POS Setting but your POS Payment Method missed add Payment Method [Rounding Amount]."),
            });
        }
        selectedOrder.paymentlines.forEach(function (p) {
            if (p.payment_method && p.payment_method.journal && p.payment_method.journal.pos_method_type == 'rounding') {
                selectedOrder.remove_paymentline(p)
            }
        })
        let due = selectedOrder.get_due();
        let sign = Math.sign(due);
        let amountRound = 0;
        if (this.pos.config.rounding_automatic_type == 'rounding_integer') {
            let decimal_amount = due - (sign * (Math.floor(Math.abs(due))));
            if (decimal_amount < 0.5) {
                amountRound = -decimal_amount
            } else {
                amountRound = 1 - decimal_amount;
            }
        } else if (this.pos.config.rounding_automatic_type == 'rounding_up') {
              let round_factor = this.pos.config.rounding_automatic_factor
              let after_round = sign * (Math.ceil(Math.abs(due) / round_factor) * round_factor);
              amountRound = after_round - due;
        } else if (this.pos.config.rounding_automatic_type == 'rounding_down') {
              let round_factor = this.pos.config.rounding_automatic_factor
              let after_round = sign * (Math.floor(Math.abs(due) / round_factor) * round_factor);
              amountRound = after_round - due;
        } else if (this.pos.config.rounding_automatic_type == 'rounding_up_down') {
              let round_factor = this.pos.config.rounding_automatic_factor
              let after_round = Math.round(due / round_factor) * round_factor;
              amountRound = after_round - due;
        } else {
            let after_round = Math.round(due * Math.pow(10, roundingMethod.journal.decimal_rounding)) / Math.pow(10, roundingMethod.journal.decimal_rounding);
            amountRound = after_round - due;
        }
        if (amountRound) {
            selectedOrder.add_paymentline(roundingMethod);
            let roundedPaymentLine = selectedOrder.selected_paymentline;
            roundedPaymentLine.amount = -amountRound
        }
    }

})
