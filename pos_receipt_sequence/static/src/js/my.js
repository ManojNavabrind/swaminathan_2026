// /** @odoo-module **/

// import { Order } from "@point_of_sale/app/store/models";
// import { patch } from "@web/core/utils/patch";

// // Module-level variable to track the next sequence number
// let _nextSequenceNumber = null;

// /**
//  * Parse sequence string (e.g., 'POS/0071') and return the numeric part
//  */
// function parseSequenceNumber(seqString) {
//     if (typeof seqString === "string" && seqString.includes("/")) {
//         const parts = seqString.split("/");
//         const number = parseInt(parts.pop(), 10);
//         if (!isNaN(number)) return number;
//     }
//     return null;
// }

// /**
//  * Fetch latest confirmed sequence from backend controller
//  */
// async function fetchLatestSequence(env) {
//     try {
//         const result = await env.services.rpc("/pos_sequence/latest", {});
//         console.log("Backend latest sequence:", result.receipt_sequence);
//         const latestNumber = parseSequenceNumber(result.receipt_sequence);
//         if (latestNumber !== null) {
//             _nextSequenceNumber = latestNumber + 1;
//         } else {
//             _nextSequenceNumber = 1;
//         }
//         console.log("Next sequence number set to:", _nextSequenceNumber);
//     } catch (e) {
//         console.error("Failed to fetch latest POS sequence from backend:", e);
//         _nextSequenceNumber = 1; // fallback
//     }
// }

// patch(Order.prototype, {

//     /**
//      * Setup is called when a new Order instance is created
//      */
//     async setup(obj, options) {
//         await super.setup(...arguments);
//         console.log("Order setup called. Current sequence:", this.receipt_sequence);

//         // Always fetch the latest sequence if not yet set
//         if (_nextSequenceNumber === null && this.env?.services) {
//             await fetchLatestSequence(this.env);
//         }

//         // Generate receipt_sequence only after backend fetch
//         if (!this.receipt_sequence) {
//             this.receipt_sequence = this._generateNextSequence();
//             console.log("Generated receipt_sequence:", this.receipt_sequence);
//         }
//     },

//     /**
//      * Generate next sequence string
//      */
//     _generateNextSequence() {
//         if (_nextSequenceNumber === null) {
//             _nextSequenceNumber = 1;
//         }
//         const padded = String(_nextSequenceNumber++).padStart(5, "0");
//         const sequence = `POS/${padded}`;
//         console.log("Next temporary sequence:", sequence);
//         return sequence;
//     },

//     /**
//      * Load order data from backend JSON
//      */
//     init_from_JSON(json) {
//         super.init_from_JSON(...arguments);
//         if (json.receipt_sequence) {
//             console.log("Loading sequence from JSON:", json.receipt_sequence);
//             this.receipt_sequence = json.receipt_sequence;
//             const num = parseSequenceNumber(this.receipt_sequence);
//             if (num !== null && (!_nextSequenceNumber || num >= _nextSequenceNumber)) {
//                 _nextSequenceNumber = num + 1;
//                 console.log("Updated _nextSequenceNumber from JSON:", _nextSequenceNumber);
//             }
//         }
//     },

//     /**
//      * Include receipt_sequence in export JSON to backend
//      */
//     export_as_JSON() {
//         const json = super.export_as_JSON(...arguments);
//         json.receipt_sequence = this.receipt_sequence;
//         console.log("export_as_JSON - receipt_sequence:", this.receipt_sequence);
//         return json;
//     },

//     /**
//      * Include receipt_sequence in printable receipt data
//      */
//     export_for_printing() {
//         const result = super.export_for_printing(...arguments);
//         result.headerData.receipt_sequence = this.receipt_sequence;
//         console.log("export_for_printing - receipt_sequence:", this.receipt_sequence);
//         return result;
//     },

//     /**
//      * Utility to manually refresh backend sequence if needed
//      * Call this anytime to sync with backend
//      */
//     async refreshSequenceFromBackend() {
//         if (this.env?.services) {
//             await fetchLatestSequence(this.env);
//             console.log("Manually refreshed sequence from backend. Next:", _nextSequenceNumber);
//         }
//     },
// });


// Get Value from new field
/** @odoo-module **/
import { Order } from "@point_of_sale/app/store/models";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json.receipt_sequence) {
            this.receipt_sequence = json.receipt_sequence;
        }
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.receipt_sequence = this.receipt_sequence;
        return json;
    },

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.headerData = result.headerData || {};
        result.headerData.receipt_sequence = this.receipt_sequence || "";
        return result;
    },
});

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        const pushedOrders = await this.pos.push_single_order(order);
        if (pushedOrders && pushedOrders.length) {
            const backendOrder = pushedOrders[0];
            order.receipt_sequence = backendOrder.receipt_sequence;
        }
        await super.validateOrder(...arguments);
    },
});
