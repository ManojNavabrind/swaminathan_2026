  /** @odoo-module **/

    import { _t } from "@web/core/l10n/translation";
    import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { useService } from "@web/core/utils/hooks";
    import { Component } from "@odoo/owl";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

    export class ChangeUOMButton extends Component {
        static template = "sh_pos_secondary.ChangeUOMButton";
        setup() {
            this.pos = usePos();
            this.popup = useService("popup");
        }
        async onClickUOM() {
            var selectionList = [];
            var line = this.pos.get_order().get_selected_orderline();
            if (line) {
                var uom = line.get_unit();
                if (uom) {
                    selectionList.push({ id: uom.id, isSelected: true, label: uom.display_name, item: uom });
                    var secondary_uom = line.get_secondary_unit();
                    if (secondary_uom != uom) {
                        selectionList.push({ id: secondary_uom.id, isSelected: false, label: secondary_uom.display_name, item: secondary_uom });
                    }
                }
            }
            for(let each_uom of selectionList){
                if (each_uom.label === line.get_current_uom().name) {
                    each_uom.isSelected = true;
                } else {
                    each_uom.isSelected = false;
                }
            };
            const { confirmed, payload: selectedUOM } = await this.popup.add(
                SelectionPopup,
                {
                    title: _t("Select the UOM"),
                    list: selectionList,
                }
            );
            if (confirmed) {
                line.change_current_uom(selectedUOM);
            }
        }
    }

    ProductScreen.addControlButton({
        component: ChangeUOMButton,
        condition: function () {
            return true
        },
    })
