/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Orderline } from  "@point_of_sale/app/store/models";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";

patch(Orderline.prototype, {

     get_price_with_tax() {
        let price_subtotal_incl =  super.get_price_with_tax(...arguments);
        let sign = Math.sign(price_subtotal_incl);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                price_subtotal_incl = sign * (Math.ceil(Math.abs(price_subtotal_incl) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                price_subtotal_incl = sign * (Math.floor(Math.abs(price_subtotal_incl) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                price_subtotal_incl = round_pr(price_subtotal_incl, round_factor);
            }
        }
        return price_subtotal_incl;
     },

     get_price_without_tax() {
        let price_subtotal =  super.get_price_without_tax(...arguments);
        let sign = Math.sign(price_subtotal);
        if (this.pos.config.rounding) {
            if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                price_subtotal = sign * (Math.ceil(Math.abs(price_subtotal) / round_factor) * round_factor);
            } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                price_subtotal = sign * (Math.floor(Math.abs(price_subtotal) / round_factor) * round_factor);
            } else{
                let round_factor = this.pos.config.rounding_factor;
                price_subtotal = round_pr(price_subtotal, round_factor);
            }
        }
        return price_subtotal;
     },

     get_all_prices(qty = this.get_quantity()) {
         let all_prices = super.get_all_prices(...arguments);
         let signWithTax = Math.sign(all_prices['priceWithTax']);
         let signWithoutTax = Math.sign(all_prices['priceWithoutTax']);
         if (this.pos.config.rounding) {
             if (this.pos.config.rounding_type == 'rounding_up'){
                let round_factor = this.pos.config.rounding_factor;
                all_prices['priceWithTax'] = signWithTax * (Math.ceil(Math.abs(all_prices['priceWithTax']) / round_factor) * round_factor);
                all_prices['priceWithoutTax']  = signWithoutTax * (Math.ceil(Math.abs(all_prices['priceWithoutTax'])  / round_factor) * round_factor);
             } else if(this.pos.config.rounding_type == 'rounding_down'){
                let round_factor = this.pos.config.rounding_factor;
                all_prices['priceWithTax'] = signWithTax * (Math.floor(Math.abs(all_prices['priceWithTax']) / round_factor) * round_factor);
                all_prices['priceWithoutTax']  = signWithoutTax * (Math.floor(Math.abs(all_prices['priceWithoutTax'])  / round_factor) * round_factor);
             } else{
                let round_factor = this.pos.config.rounding_factor;
                all_prices['priceWithTax'] = round_pr(all_prices['priceWithTax'], round_factor);
                all_prices['priceWithoutTax'] = round_pr(all_prices['priceWithoutTax'], round_factor);
             }
         }
         return all_prices
     }
})