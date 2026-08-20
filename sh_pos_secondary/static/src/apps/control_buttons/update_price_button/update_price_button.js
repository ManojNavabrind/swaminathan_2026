    /** @odoo-module */
    import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { UpdateQtyPopup } from "@sh_pos_secondary/apps/control_buttons/update_price_button/price_window";
    import { useService } from "@web/core/utils/hooks";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { _t } from "@web/core/l10n/translation";
    import { Component } from "@odoo/owl";
    /**
    * This class represents a custom button in the Point of Sale product screen.
    */
    export class UpdateQty extends Component {
       static template = "sh_pos_secondary.UpdateQty";
       setup() {
           this.pos = usePos();
           this.popup = useService("popup");
       }

    async click() {
    const getEle = document.querySelector('.selected #secondary_qty');

    if (!getEle) {
        console.error('Element with selector ".selected #secondary_qty" not found.');
        return;
    }

    const order = this.pos.get_order();
    var line = this.pos.get_order().get_selected_orderline();
    var product = line.get_product();
    var secondary_uom = line.get_secondary_unit();

    let factor = parseFloat(getEle.innerText);
    if (!isNaN(factor)) {
        factor = Math.round(factor);
    }

    await this.popup.add(UpdateQtyPopup, {
        title: _t("Update Quantity"),
        secondary_uom: secondary_uom,
        factor: factor,
        selectedProduct: product['display_name'],
    });
}
    }
    // Adds the custom button to the ProductScreen controls.
    ProductScreen.addControlButton({
       component: UpdateQty,
       condition: function () {
           return true;
       },
    });
