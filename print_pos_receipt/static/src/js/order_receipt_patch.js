/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

function computeBillTypeFromReceiptData(data) {
    let isRefund = false;

    if (data.orderlines) {
        for (const line of data.orderlines) {
            if (line.qty < 0) {
                isRefund = true;
                break;
            }
        }
    }

    return isRefund ? "REFUND BILL" : "CASH BILL";
}

patch(Order.prototype, {

    export_for_printing() {
        const data = super.export_for_printing(...arguments);

        // ⭐ compute using receipt JSON (important)
        const billType = computeBillTypeFromReceiptData(data);

        if (!data.headerData) data.headerData = {};
        data.headerData.bill_type = billType;

        // preview renderer uses root
        data.bill_type = billType;

        return data;
    },

});
