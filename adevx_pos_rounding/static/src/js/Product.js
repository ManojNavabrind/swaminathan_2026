/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {Product} from "@point_of_sale/app/store/models";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";

patch(Product.prototype, {

    get_price(pricelist, quantity, price_extra = 0, recurring = false) {
        let price = super.get_price(pricelist, quantity, price_extra, recurring)
        let sign = Math.sign(price);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                price = sign * (Math.ceil(Math.abs(price) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                price = sign * (Math.floor(Math.abs(price) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                price = round_pr(price, round_factor);
            }
        }
        return price
    }

})