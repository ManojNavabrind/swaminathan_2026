/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";


patch(PaymentScreen.prototype, {
     async roundingTotalPaid() {
        let selectedOrder = this.currentOrder;
        let roundingMethod = this.pos.payment_methods.find((p) => p.journal && p.journal.pos_method_type == 'rounding')
        if (!selectedOrder || !roundingMethod) {
             return this.popup.add(ErrorPopup, {
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
        if (due == 0) {
            return this.popup.add(ErrorPopup, {
                title: _t("Warning"),
                body: _t("Due Amount is 0, please remove all payments register the first."),
            });
        }
        let amountRound = 0;
        if (this.pos.config.rounding_automatic_type == 'rounding_integer') {
            let decimal_amount = due - (sign * (Math.floor(Math.abs(due))));
            if (decimal_amount <= 0.25) {
                amountRound = -decimal_amount
            } else if (decimal_amount > 0.25 && decimal_amount < 0.75) {
                amountRound = 1 - decimal_amount - 0.5;
                amountRound = 0.5 - decimal_amount;
            } else if (decimal_amount >= 0.75) {
                amountRound = 1 - decimal_amount
            }
        } else if (this.pos.config.rounding_automatic_type == 'rounding_up') {
            let decimal_amount = due - (sign * (Math.floor(Math.abs(due))));
            amountRound = 1 - decimal_amount;
        } else if (this.pos.config.rounding_automatic_type == 'rounding_down') {
            let decimal_amount = due - (sign * (Math.floor(Math.abs(due))));
            amountRound = -decimal_amount
        } else if (this.pos.config.rounding_automatic_type == 'rounding_up_down') {
            let decimal_amount = due - (sign * (Math.floor(Math.abs(due))));
            if (decimal_amount < 0.5) {
                amountRound = -decimal_amount
            } else {
                amountRound = 1 - decimal_amount;
            }
        } else {
            let after_round = Math.round(due * Math.pow(10, roundingMethod.journal.decimal_rounding)) / Math.pow(10, roundingMethod.journal.decimal_rounding);
            amountRound = after_round - due;
        }
        if (amountRound == 0) {
             this.popup.add(ErrorPopup, {
                title: _t("Warning"),
                body: _t("Total Paid of Order have not any rounding Amount."),
            });
        } else {
            selectedOrder.add_paymentline(roundingMethod);
            let roundedPaymentLine = selectedOrder.selected_paymentline;
            roundedPaymentLine.set_amount(-amountRound);
        }
    },
});