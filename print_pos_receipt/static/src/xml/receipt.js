/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { omit } from "@web/core/utils/objects";

export class OrderReceiptPos extends Component {

    static template = "print_pos_receipt.OrderReceipt";
    static components = {
        Orderline,
        OrderWidget,
        ReceiptHeader,
    };
    static props = {
        data: Object,
        formatCurrency: Function,
    };
    omit(...args) {
        return omit(...args);
    }
}

registry.category("pos_screens").add("OrderReceiptPos", OrderReceiptPos);
