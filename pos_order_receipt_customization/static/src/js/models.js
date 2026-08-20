/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

//import { Orderline } from "@point_of_sale/app/models/pos_order_line";
//Orderline.prototype.get_taxes = function () {
//    let taxes = [];
//    if (this.get_product().taxes_id) {
//        let allTaxes = this.pos.taxes;
//        this.get_product().taxes_id.forEach((tax_id) => {
//            let tax = allTaxes.find(t => t.id === tax_id);
//            if (tax) {
//                let taxAmount = (this.get_display_price() * tax.amount) / 100;
//                taxes.push({
//                    name: tax.name,
//                    amount: taxAmount,
//                });
//
//            }
//        });
//    } console.log("ytr",taxes);
//
//    return taxes;
//};

patch(Orderline.prototype, {
    getDisplayData() {
        const json = super.getDisplayData(...arguments);
        if (json) {
            const product = this.get_product() || {};
            json.product = product;
            json.bottle_type = product.bottle_type || "";
            json.varient_type = product.varient_type || "";
            json.detailed_type = product.detailed_type || product.type || "";  // ✅ added
            json.price_with_tax = this.env.utils.formatCurrency(this.get_price_with_tax()) || "";
        }
        return json;
    },
});


//patch(Order.prototype, {
//    export_for_printing() {
//        const result = super.export_for_printing(...arguments);
//        const orders = this.orderlines;
//
//        let totalDiscount = 0;
//
//        orders.forEach(line => {
//            // Case 2: DSC product line
//          if (line.get_product()) {
//                totalDiscount = Math.abs(line.get_price_with_tax());
//            }
//        });
//
////        result.discount_value = this.env.utils.formatCurrency(totalDiscount);
//          result.discount_value = this.env.utils.formatCurrency(totalDiscount);
//          result.total_without_discount = this.get_total_with_tax() + totalDiscount;
//
//        console.log("Overall discount (currency):", result.discount_value);
//        console.log("Total w/o discount:", result.total_without_discount);
//        return result;
//    },
//});

patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        const orders = this.orderlines;

        let totalDiscount = 0;

        orders.forEach(line => {
            const product = line.get_product();
            if (product && product.default_code === "DSC") {
                const discountAmount = Math.abs(line.get_price_with_tax());
                if (discountAmount > 0) {
                    totalDiscount += discountAmount;
                }
            }
        });

        if (totalDiscount > 0) {
            result.discount_value = this.env.utils.formatCurrency(totalDiscount);
            result.total_without_discount = this.get_total_with_tax() + totalDiscount;
        } else {
            // no DSC product → no discount field in result
            result.discount_value = null;
            result.total_without_discount = this.get_total_with_tax();
        }

        console.log("Overall discount (currency):", result.discount_value || "No discount");
        console.log("Total w/o discount:", result.total_without_discount);
        return result;
    },
});






