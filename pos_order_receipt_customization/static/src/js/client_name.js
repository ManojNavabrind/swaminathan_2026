/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import {
    formatDate,
    formatDateTime,
    serializeDateTime,
    deserializeDate,
    deserializeDateTime,
} from "@web/core/l10n/dates";
const { DateTime } = luxon;

patch(Order.prototype, {
   export_for_printing() {
       const result = super.export_for_printing(...arguments);

//       sec_uom = this.get_secondary_unit()
//        console.log(sec_uom,'tttttttttttttteeeeeeeeee')
       if (this.get_partner()) {
           result.headerData.partner = this.get_partner();
           }

        result.headerData.date = DateTime.now().toFormat('dd-MM-yyyy HH:mm:ss');


            result.headerData.name = this.get_name();

//       if (name){
//        result.headerDate.name = name;
//       }
       return result;
   },
});
