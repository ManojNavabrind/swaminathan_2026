/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useRef, onMounted } from "@odoo/owl";
import { Order, Orderline , Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

export class UpdateQtyPopup extends AbstractAwaitablePopup {
   static template = "sh_pos_secondary.UpdateQtyPopup";
   static defaultProps = {
       closePopup: _t("Cancel"),
       confirmText: _t("Update"),
       title: _t("Update Quantity"),
   };

   setup() {
           this.pos = usePos();
       }


   async update() {
    var updated = 'True';
    var lines = this.pos.get_order().get_selected_orderline();
    if (lines.length === 0) return; // Exit if no lines are selected

    var productId = lines.product['id'];
    var quant1 = parseFloat($(".quantity_input").val());
    var existingData = JSON.parse(localStorage.getItem('updateData')) || {};
    var arr = Object.keys(existingData).map(key => existingData[key]);
    var productExists = arr.find(item => item.id == productId);

    lines.manual_factor = quant1;

    if (productExists) {
        productExists.update_qty = quant1;
    } else {
        arr.push({ id: productId, update_qty: quant1 });
    }
    localStorage.setItem('updateData', JSON.stringify(arr));
    const getEle = document.querySelector('.selected #secondary_qty');
    const inputEle = document.querySelector('.quantity_input');

    if(getEle){
       if(inputEle) {
       getEle.innerText = inputEle.value;
       inputEle.value = getEle.innerText;
       };

    }

    this.cancel();
    return true;
}
}







