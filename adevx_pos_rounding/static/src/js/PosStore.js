/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {

    async setup() {
        await super.setup(...arguments);
        if (this.config.rounding) {
            for (let decimal_name in this.dp) {
                if (decimal_name == 'Product Price') {
                    this.dp[decimal_name] = this.config.decimal_places;
                }
            }
        }
    },

})