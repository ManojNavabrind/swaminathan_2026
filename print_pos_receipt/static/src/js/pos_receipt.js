/** @odoo-module */

import { Component } from "@odoo/owl";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

export class PrintReceiptButton extends Component {
    static template = "print_pos_receipt.PrintReceiptButton";

    setup() {
        this.pos = usePos();
        this.printer = useService("printer");
    }

    async printReceipt() {
        const order = this.pos.get_order();

        if (!order) {
            console.warn("No order found to print.");
            return;
        }

        const orderData = order.export_for_printing();

        let billType = "CASH BILL";

        // ✅ Detect Refund (most reliable method)
        const isRefund = order
            .get_orderlines()
            .some(line => line.get_quantity() < 0);

        if (isRefund) {
            billType = "REFUND BILL";
        }
        // ✅ Detect Estimate (no payment lines)
        else if (order.get_paymentlines().length === 0) {
            billType = "ESTIMATE BILL";
        }

        // ✅ VERY IMPORTANT — Put inside headerData
        orderData.headerData = orderData.headerData || {};
        orderData.headerData.bill_type = billType;

        // ✅ Change PDF title
        const originalTitle = document.title;
        document.title = billType;

        await this.printer.print(
            OrderReceipt,
            {
                data: orderData,
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );

        document.title = originalTitle;
    }
}

ProductScreen.addControlButton({
    component: PrintReceiptButton,
    condition: function () {
        return true;
    },
});

export default PrintReceiptButton;
