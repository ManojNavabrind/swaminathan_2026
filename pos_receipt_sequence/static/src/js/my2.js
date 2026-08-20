// // working storage

// /** @odoo-module **/

// import { Order } from "@point_of_sale/app/store/models";
// import { patch } from "@web/core/utils/patch";

// // Key for storing the temporary counter in sessionStorage
// const TEMP_SEQUENCE_KEY = 'pos_temporary_sequence_counter';

// /**
//  * Loads the last used temporary counter from sessionStorage.
//  * If not found, it starts at 1.
//  * @returns {number} The starting counter value.
//  */
// function getInitialCounter() {
//     const savedValue = sessionStorage.getItem(TEMP_SEQUENCE_KEY);
//     // Use the saved value (parsed as an integer), or default to 1
//     return savedValue ? parseInt(savedValue, 10) : 1;
// }

// // Module-level variable to track the temporary local sequence number.
// // It is initialized from sessionStorage to maintain continuity across reloads.
// let _temporarySequenceCounter = getInitialCounter();

// /**
//  * Patches the Order prototype to handle the 'receipt_sequence' field.
//  * - Generates a temporary 'POS/' sequence ID for new orders on the client side (sequential and locally incrementing).
//  * - Loads the final, permanent sequence (POS/0001) from the backend upon syncing.
//  * - Exports the sequence for printing and saving to the backend.
//  */
// patch(Order.prototype, {

//     /**
//      * Helper to generate a sequential, temporary client-side sequence ID.
//      * This ID is used for orders before they are submitted to the backend 
//      * and receive the permanent sequence defined in 'pos.receipt.sequence'.
//      * @returns {string} The temporary sequence ID (e.g., POS/0001, POS/0002...).
//      */
//     _generateTemporaryReceiptSequence() {
//         // Use the sequential counter and pad it to 4 digits
//         const paddedSequence = String(_temporarySequenceCounter).padStart(4, '0');
        
//         // Save the counter and increment it for the next order
//         sessionStorage.setItem(TEMP_SEQUENCE_KEY, ++_temporarySequenceCounter);

//         // New format: POS/XXXX (sequential, local counter)
//         return `POS/${paddedSequence}`;
//     },
    
//     /**
//      * Override setup to initialize the field for new orders.
//      * If no receipt_sequence is present, generate a temporary one immediately.
//      */
//     setup(obj, options) {
//         super.setup(...arguments);
//         // Initialize the field or keep the existing value if loaded
//         this.receipt_sequence = this.receipt_sequence || null;

//         // If it's a new order and the sequence is missing, generate the temporary ID.
//         if (!this.receipt_sequence) {
//             this.receipt_sequence = this._generateTemporaryReceiptSequence();
//         }
//     },

//     /**
//      * Override to load the receipt_sequence from backend data.
//      * This is called when an existing order is loaded (e.g., after the payment 
//      * process returns the order with the final sequence number).
//      */
//     init_from_JSON(json) {
//         super.init_from_JSON(...arguments);
//         // Load the permanent sequence (e.g., POS/00001) from the backend JSON, overwriting the temporary one.
//         this.receipt_sequence = json.receipt_sequence || this.receipt_sequence; 

//         // CRITICAL: If a permanent sequence is loaded, we update the local temporary counter.
//         // This ensures the temporary counter starts *after* the last known permanent sequence
//         // in case the user closes and re-opens the POS screen during operation.
//         if (this.receipt_sequence && !this.receipt_sequence.startsWith('POS/')) {
//             const parts = this.receipt_sequence.split('/');
//             const number = parseInt(parts[1], 10);
            
//             // Check if the permanent sequence number is higher than our current local counter.
//             if (!isNaN(number) && number >= _temporarySequenceCounter) {
//                 // Set the next temporary counter to be one greater than the permanent one
//                 _temporarySequenceCounter = number + 1;
//                 sessionStorage.setItem(TEMP_SEQUENCE_KEY, _temporarySequenceCounter);
//             }
//         }
//     },

//     /**
//      * Override to include the receipt_sequence in the data sent to the backend.
//      */
//     export_as_JSON() {
//         const json = super.export_as_JSON(...arguments);
//         // The backend will use this field to store the permanent sequence
//         json.receipt_sequence = this.receipt_sequence;
//         return json;
//     },

//     /**
//      * Override to include the receipt_sequence in the receipt's printable data.
//      */
//     export_for_printing() {
//         const result = super.export_for_printing(...arguments);
//         // Make the sequence available in the receipt template (XML)
//         result.headerData.receipt_sequence = this.receipt_sequence;
//         return result;
//     },
// });