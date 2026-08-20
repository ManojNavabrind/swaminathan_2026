/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Payment } from "@point_of_sale/app/store/models";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";

patch(Payment.prototype, {

    set_amount() {
        super.set_amount(...arguments);
        let sign = Math.sign(this.amount);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                this.amount = sign * (Math.ceil(Math.abs(this.amount) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                this.amount = sign * (Math.floor(Math.abs(this.amount) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                this.amount = round_pr(this.amount, round_factor);
            }
        }
    }

})