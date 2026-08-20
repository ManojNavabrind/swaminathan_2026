/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

// Log to confirm patch loads
console.log("✅ POS discount patch loaded");

patch(Orderline.prototype, {
    getDisplayData() {
        const json = super.getDisplayData(...arguments);
        if (json) {
            // Ensure discount is always a string
            const discount = this.get_discount?.() ?? 0;
            json.discount = String(discount);

            // Optional: keep other fields
            const product = this.get_product?.() || {};
            json.product = product;
            json.price_with_tax = this.env.utils.formatCurrency(this.get_price_with_tax?.() || 0);
        } else {
            return { discount: "0" };
        }
        return json;
    },
});
