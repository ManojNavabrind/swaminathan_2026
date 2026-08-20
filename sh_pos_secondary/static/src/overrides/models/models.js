/** @odoo-module */
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";
import { Order, Orderline , Product } from "@point_of_sale/app/store/models";

const { DateTime } = luxon;
import { patch } from "@web/core/utils/patch";
   document.addEventListener("click", function(event) {
    const isElements = document.querySelectorAll(".numpad_btn");
    const isCancel = !!event.target.closest(".numpad_btn");
    let getId;

    if (isCancel) {
        if (event.target.innerText == "⌫") {
            // Retrieve data from localStorage and ensure it is not null
            let val = JSON.parse(localStorage.getItem("updateData")) || [];

            const getId_val = document.querySelector(".selected #getSelectedId");
            if (getId_val) {
                getId = getId_val.innerText;
            }

            if (getId && val.length > 0) {
                // Find the index of the item with the matching id
                let find_val = val.findIndex((item) => item.id == getId);

                if (find_val !== -1) { // Ensure the item is found
                    const getUnit = document.querySelector(".selected .price-per-unit em").innerText;
                    if (getUnit == "0.000") {
                        val.splice(find_val, 1); // Remove the item from the array
                        localStorage.setItem('updateData', JSON.stringify(val)); // Update localStorage
                    }
                }
            }
        }
    }
});


patch(Product.prototype, {
   get_sec_price(pricelist,factor, quantity, uom, price_extra = 0, recurring = false) {
    const date = DateTime.now();
    if (recurring && !pricelist) {
        alert(
            _t(
                "An error occurred when loading product prices. " +
                "Make sure all pricelists are available in the POS."
            )
        );
    }

    const rules = !pricelist
        ? []
        : (this.applicablePricelistItems[pricelist.id] || []).filter((item) =>
            this.isPricelistItemUsable(item, date)
        );

    let price = this.lst_price + (price_extra || 0)
    if (uom) {
        if (this.uom_id[1] == uom) {
            price = this.lst_price + (price_extra || 0);
        } else if (this.secondary_uom[1] == uom) {
            price = this.secondary_sale_price + (price_extra || 0);
        } else {
            price = this.secondary_sale_price + (price_extra || 0);
        }
    }

    const rule = rules.find((rule) => !rule.min_quantity || quantity >= rule.min_quantity);
    if (!rule) {
        price = this.getEvaluationPrice(this.product_tmpl_id, price)
        return price;
    }

    if (rule.base === "pricelist") {
        const base_pricelist = this.pos.pricelists.find(
            (pricelist) => pricelist.id === rule.base_pricelist_id[0]
        );
        if (base_pricelist) {
            price = this.get_price(base_pricelist, quantity, 0, true);
        }
    } else if (rule.base === "standard_price") {
        price = this.standard_price;
    }

    if (rule.compute_price === "fixed") {
        price = rule.fixed_price;
    } else if (rule.compute_price === "percentage") {
        price = price - price * (rule.percent_price / 100);
    } else {
        var factor =  factor;
        if (pricelist.type === "retail") {
            var order = this.pos.get_order();
            if (order){

            var orderlines = order.selected_orderline;
            var factor =  orderlines.product['factor'];
            if (rule.evaluation) {
                price = price+ (price * (rule.evaluation / 100));
            }

            if (rule.expense) {
                price = price+ (price * (rule.expense / 100));
            }
            if (rule.tax_id) {
                let taxString = rule.tax_id[1];
                let taxValue =taxString.match(/\d+/)[0];
                price = price + (price * (taxValue / 100));
            }
            if (rule.margin) {
                price = price + (price * (rule.margin / 100));
            }
            price = price * orderlines.product['uom_ratio']
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
            }
        if (pricelist.type === "wholesale") {
            if (rule.evaluation) {
                price = price+ (price * (rule.evaluation / 100));
            }

            if (rule.expense) {
                price = price+ (price * (rule.expense / 100));
            }

            if (rule.margin) {
                price = price + (price * (rule.margin / 100));
            }
            if (rule.tax_id) {
                let taxString = rule.tax_id[1];
                let taxValue =taxString.match(/\d+/)[0];
                price = price + (price * (taxValue / 100));
            }
            price = price * orderlines.product['uom_ratio']
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }
        if (pricelist.type === "export") {
            if (rule.evaluation) {
                price = price+ (price * (rule.evaluation / 100));
            }

            if (rule.expense) {
                price = price+ (price * (rule.expense / 100));
            }
            if (rule.packing) {
                price = price+ (price * (rule.packing / 100));
            }
            if (rule.tax_id) {
                let taxString = rule.tax_id[1];
                let taxValue =taxString.match(/\d+/)[0];
                price = price + (price * (taxValue / 100));
            }
            if (rule.margin) {
                price = price + (price * (rule.margin / 100));
            }
            price = price * orderlines.product['uom_ratio']
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }
        }
    }

    if (price){
       price = this.getEvaluationPrice(this.product_tmpl_id, price)
    }
    return price;
},
    get_price(pricelist, quantity, uom, price_extra = 0, recurring = false) {
    const date = DateTime.now();
    if (recurring && !pricelist) {
        alert(
            _t(
                "An error occurred when loading product prices. " +
                "Make sure all pricelists are available in the POS."
            )
        );
    }

    const rules = !pricelist
        ? []
        : (this.applicablePricelistItems[pricelist.id] || []).filter((item) =>
            this.isPricelistItemUsable(item, date)
        );

    let price = this.lst_price + (price_extra || 0)
    if (uom) {
        if (this.uom_id[1] == uom) {
            price = this.lst_price + (price_extra || 0);
        } else if (this.secondary_uom[1] == uom) {
            price = this.secondary_sale_price + (price_extra || 0);
        } else {
            price = this.secondary_sale_price + (price_extra || 0);
        }
    }

    const rule = rules.find((rule) => !rule.min_quantity || quantity >= rule.min_quantity);
    if (!rule) {
        price = this.getEvaluationPrice(this.product_tmpl_id, price)
        return price;
    }

    if (rule.base === "pricelist") {
        const base_pricelist = this.pos.pricelists.find(
            (pricelist) => pricelist.id === rule.base_pricelist_id[0]
        );
        if (base_pricelist) {
            price = this.get_price(base_pricelist, quantity, 0, true);
        }
    } else if (rule.base === "standard_price") {
        price = this.standard_price;
    }

    if (rule.compute_price === "fixed") {
        price = rule.fixed_price;
    } else if (rule.compute_price === "percentage") {
        price = price - price * (rule.percent_price / 100);
    } else {
//        price = this.standard_price;
        if (pricelist.type === "retail") {
            if (rule.evaluation) {
                price = price+ (price * (rule.evaluation / 100));
            }

            if (rule.expense) {
                price = price+ (price * (rule.expense / 100));
            }
            if (rule.tax_id) {
                let taxString = rule.tax_id[1];
                let taxValue =taxString.match(/\d+/)[0];
                price = price + (price * (taxValue / 100));
            }
            if (rule.margin) {
                price = price + (price * (rule.margin / 100));
            }
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }
        if (pricelist.type === "wholesale") {
            if (rule.evaluation) {
                price = price+ (price * (rule.evaluation / 100));
            }

            if (rule.expense) {
                price = price+ (price * (rule.expense / 100));
            }

            if (rule.margin) {
                price = price + (price * (rule.margin / 100));
            }
            if (rule.tax_id) {
                let taxString = rule.tax_id[1];
                let taxValue =taxString.match(/\d+/)[0];
                price = price + (price * (taxValue / 100));
            }
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }
        if (pricelist.type === "export") {
            if (rule.evaluation) {
                price = price+ (price * (rule.evaluation / 100));
            }

            if (rule.expense) {
                price = price+ (price * (rule.expense / 100));
            }
            if (rule.packing) {
                price = price+ (price * (rule.packing / 100));
            }
            if (rule.tax_id) {
                let taxString = rule.tax_id[1];
                let taxValue =taxString.match(/\d+/)[0];
                price = price + (price * (taxValue / 100));
            }
            if (rule.margin) {
                price = price + (price * (rule.margin / 100));
            }
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }
    }

    price = this.getEvaluationPrice(this.product_tmpl_id, price)
    return price;
},
    getEvaluationPrice(product, price){
//        var result = this.orm.call("price.evaluation", "get_product_price", [[product, price]]);
        var evaluated_price = price + (price * (this.evaluation_id / 100.0))

        return evaluated_price
    },
    getFormattedUnitPrice(){
        let res = super.getFormattedUnitPrice()
        if(this.sh_secondary_uom && this.sh_is_secondary_unit && this.pos.config.enable_price_to_display && this.pos.config.select_uom_type == 'secondary' ){
            let unit_price=   this.get_display_price()
            var secondary = this.get_product_secondary_unit(this.sh_secondary_uom)
            var primary = this.pos.units_by_id[1]
            var k = this.convert_product_qty_uom(1, primary, secondary)
            return this.env.utils.formatCurrency(unit_price * k)
        }else{
            return res
        }
    },
    convert_product_qty_uom(quantity, to_uom, from_uom) {
        var to_uom = to_uom;
        var from_uom = from_uom;
        var from_uom_factor = from_uom.uom_ratio;
        var amount = quantity / from_uom_factor;
        if (to_uom) {
            var to_uom_factor = to_uom.uom_ratio;
            amount = amount * to_uom_factor;
        }

        return amount;
    },
    get_product_secondary_unit(secondary_unit_id){
        if (!secondary_unit_id) {
            return this.props.product.get_unit()
        }
        secondary_unit_id = secondary_unit_id[0];
        if (!this.pos) {
            return undefined;
        }

        return this.pos.units_by_id[secondary_unit_id];
    }
})

patch(Order.prototype, {
    set_pricelist(pricelist) {
        var self = this;
        this.pricelist = pricelist;

        var lines_to_recompute = this.get_orderlines().filter((line) => {
            return !line.price_manually_set;
        });
        lines_to_recompute.forEach((line) => {
            var primary_uom = line.get_unit();
            var secondary_uom = line.get_secondary_unit();
            var current_uom = line.get_current_uom() || primary_uom;
            if (current_uom == primary_uom) {
                line.set_unit_price(line.product.get_price(self.pricelist, line.get_quantity()));
                self.fix_tax_included_price(line);
            } else {
                line.set_unit_price(line.product.get_price(self.pricelist, line.get_primary_quantity()));
                self.fix_tax_included_price(line);
            }
        });
    }
});

patch(Orderline.prototype, {

    async setup(obj, options) {
        await super.setup(obj, options)
        this.is_secondary = false
        this.update_qty = this.update_qty || null;
        if (options.price) {
            this.set_unit_price(options.price);
        } else {
            var primary_uom = this.get_unit();
            var secondary_uom = this.get_secondary_unit();
            var current_uom = this.get_current_uom() || primary_uom;
            // Initialization of price unit
            if( this.pos.config.select_uom_type == "secondary" ) {
                this.change_current_uom(secondary_uom)

                this.set_quantity(1)

            }
        }
    },

    get_unit() {
        var unit_id = this.product.uom_id;
        if (!unit_id) {
            return undefined;
        }
        unit_id = unit_id[0];
        if (!this.pos) {
            return undefined;
        }

        return this.pos.units_by_id[unit_id];
    },
    get_secondary_unit() {
        var secondary_unit_id = this.product.secondary_uom;

        if (!secondary_unit_id) {
            return this.get_unit();
        }
        secondary_unit_id = secondary_unit_id[0];
        if (!this.pos) {
            return undefined;
        }

        return this.pos.units_by_id[secondary_unit_id];
    },
    async set_quantity(quantity, keep_price) {
        this.order.assert_editable();

        var set_qty = await super.set_quantity(...arguments);
        var primary_uom = this.get_unit();
        var current_uom = this.get_current_uom() || primary_uom;
            if (current_uom == primary_uom) {
                this._initial_qty = this.quantity

                }

        if (!this.refunded_orderline_id) {
            if (this.pos.config.select_uom_type != 'secondary') {
                var secondary_uom = primary_uom;
                if (this.order.orderlines.includes(this)) {
                    this.is_secondary = true
                    secondary_uom = this.get_secondary_unit();
                }
            } else {
                this.is_secondary = true
                var secondary_uom = this.get_secondary_unit();
            }
            if (this.get_current_uom() == undefined) {
                this.set_current_uom(secondary_uom);
            }

            var current_uom = this.get_current_uom() || primary_uom;
            if (current_uom == primary_uom) {
                this.set_current_uom(primary_uom);
                this.set_primary_quantity(this.get_quantity());
                var converted_qty = this.convert_qty_uom(this.quantity, secondary_uom, current_uom);
                var line = this.pos;

                if (window.popupQuantity) {
                        sec_qty = parseFloat(window.popupQuantity);

                        var sec_qty = sec_qty
                        }

                else{
                    var sec_qty = this.quantity * this.product.uom_ratio

                    }
                this.set_secondary_quantity(sec_qty);
                if (!keep_price && !this.price_manually_set) {
                    this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
                    this.order.fix_tax_included_price(this);
                }
            } else {

                var converted_qty = this.convert_qty_uom(this.quantity, primary_uom, current_uom);
                var qty = this.quantity / this.product.uom_ratio
                this.set_primary_quantity(this._initial_qty);
                this.set_secondary_quantity(this.get_quantity());
                this.set_current_uom(secondary_uom);
                var vall = this.product.get_price(this.order.pricelist, this.get_quantity());
                if (!keep_price && !this.price_manually_set) {
                    this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
                    this.order.fix_tax_included_price(this);
                }
            }
        }

        return set_qty
    },

    convert_qty_uom(quantity, to_uom, from_uom) {
        var to_uom = to_uom;
        var from_uom = from_uom;
        var from_uom_factor = from_uom.factor;
        if (this.product.uom_id.name == from_uom.name){
            var amount = quantity;
            }
        else {
            var amount = quantity * this.product.factor;
        }

        return amount;
    },
    set_secondary_quantity(secondary_quantity, keep_price) {
        this.order.assert_editable();
        var quant = parseFloat(secondary_quantity) || 0;
        this.secondary_quantity = quant;

    },
    set_primary_quantity(primary_quantity, keep_price) {
        this.order.assert_editable();
        var quant = parseFloat(primary_quantity) || 0;
        this.primary_quantity = quant;
    },
    get_secondary_quantity() {
        return this.secondary_quantity;
    },

    get_primary_quantity() {
        return this.primary_quantity;
    },

    set_current_uom(uom_id) {
        this.order.assert_editable();
        this.current_uom = uom_id;
    },
    change_current_uom(uom_id) {
        this.order.assert_editable();
        this.current_uom = uom_id;
        if (this.current_uom == this.get_unit()) {
            this.set_quantity(this.get_primary_quantity());
        } else {
            this.set_quantity(1.000);
        }
    },
    get_current_uom() {
        return this.current_uom || this.get_unit();
    },
    get_base_price() {
        var rounding = this.pos.currency.rounding;
        var primary_uom = this.get_unit();
        var current_uom = this.get_current_uom() || primary_uom;
        // computation of base price
        if (current_uom == primary_uom) {
            return round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount() / 100), rounding);
        } else {
            return round_pr(this.get_unit_price() * this.get_primary_quantity() * (1 - this.get_discount() / 100), rounding);
        }
    },
//    get_all_prices(qty = this.get_quantity()) {
//        var self = this;
//        var product = this.get_product();
//        var factor = product.uom_ratio
//        var price_unit = this.get_unit_price() * (1.0 - this.get_discount() / 100.0);
//        var current_uom = this.get_current_uom() || primary_uom;
//        var sec_uom_price = this.product.get_sec_price(this.order.pricelist, this.get_quantity()) * (1.0 - this.get_discount() / 100.0);
//        var sec_price_discount = this.product.get_sec_price(this.order.pricelist, this.get_quantity())
//        var taxtotal = 0;
//        var product = this.get_product();
//        var taxes_ids = this.tax_ids || product.taxes_id;
//        taxes_ids = taxes_ids.filter((t) => t in this.pos.taxes_by_id);
//        var taxdetail = {};
//        var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);
//        var primary_uom = this.get_unit();
//        var secondary_uom = this.get_secondary_unit();
//        var current_uom = this.get_current_uom() || primary_uom;
//        if (current_uom == primary_uom) {
//            var all_taxes = this.compute_all(product_taxes, price_unit, qty, this.pos.currency.rounding);
//            var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), this.get_quantity(), this.pos.currency.rounding);
//        } else {
//            var sh_qty = this.get_primary_quantity() / qty
//            var all_taxes = this.compute_all(product_taxes, sec_uom_price, qty, this.pos.currency.rounding);
//            var all_taxes_before_discount = this.compute_all(product_taxes, sec_price_discount, this.get_quantity(), this.pos.currency.rounding);
//        }
//
//        all_taxes.taxes.forEach(function (tax) {
//            taxtotal += tax.amount;
//            taxdetail[tax.id] = tax.amount;
//        });
//
//
//        return {
//            priceWithTax: all_taxes.total_included,
//            priceWithoutTax: all_taxes.total_excluded,
//            priceSumTaxVoid: all_taxes.total_void,
//            priceWithTaxBeforeDiscount: all_taxes_before_discount.total_included,
//            tax: taxtotal,
//            taxDetails: taxdetail,
//        };0
//    },

            get_all_prices(qty = this.get_quantity()) {
                // Defensive checks to prevent POS crashes
                if (!this || !this.product) {
                    console.warn("⚠️ get_all_prices(): Missing product or line context:", this);
                    return {
                        priceWithTax: 0,
                        priceWithoutTax: 0,
                        priceSumTaxVoid: 0,
                        priceWithTaxBeforeDiscount: 0,
                        tax: 0,
                        taxDetails: {},
                    };
                }

                const product = this.product;
                const pricelist = this.order?.pricelist;
                if (!pricelist) {
                    console.warn("⚠️ get_all_prices(): Missing pricelist for product:", product.display_name);
                }

                const qtyToUse = qty || 1.0;
                const primary_uom = this.get_unit();
                const current_uom = this.get_current_uom() || primary_uom;

                let sec_uom_price = 0;
                try {
                    sec_uom_price = product.get_sec_price(pricelist, qtyToUse) * (1.0 - this.get_discount() / 100.0);
                } catch (err) {
                    console.warn("⚠️ get_all_prices(): get_sec_price() failed for product:", product.display_name, err);
                    sec_uom_price = this.get_unit_price();
                }

                const price_unit = this.get_unit_price() * (1.0 - this.get_discount() / 100.0);
                const taxes_ids = (this.tax_ids || product.taxes_id || []).filter((t) => t in this.pos.taxes_by_id);
                const taxdetail = {};
                const product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order?.fiscal_position);

                let all_taxes, all_taxes_before_discount, taxtotal = 0;
                if (current_uom === primary_uom) {
                    all_taxes = this.compute_all(product_taxes, price_unit, qtyToUse, this.pos.currency.rounding);
                    all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), qtyToUse, this.pos.currency.rounding);
                } else {
                    const sec_price_discount = product.get_sec_price(pricelist, qtyToUse);
                    all_taxes = this.compute_all(product_taxes, sec_uom_price, qtyToUse, this.pos.currency.rounding);
                    all_taxes_before_discount = this.compute_all(product_taxes, sec_price_discount, qtyToUse, this.pos.currency.rounding);
                }

                all_taxes.taxes.forEach(function (tax) {
                    taxtotal += tax.amount;
                    taxdetail[tax.id] = tax.amount;
                });

                return {
                    priceWithTax: all_taxes.total_included,
                    priceWithoutTax: all_taxes.total_excluded,
                    priceSumTaxVoid: all_taxes.total_void,
                    priceWithTaxBeforeDiscount: all_taxes_before_discount.total_included,
                    tax: taxtotal,
                    taxDetails: taxdetail,
                };
            },

    export_as_JSON() {
        var vals = super.export_as_JSON(...arguments);
        let data = JSON.parse(localStorage.getItem("updateData"));
        if (this.get_current_uom() && this.get_current_uom() != this.get_unit()) {
            vals["qty"] = this._initial_qty;
            vals["secondary_qty"] = this.get_quantity();
            if (this.is_secondary || this.pos.config.select_uom_type == "secondary") {
                vals["secondary_uom_id"] = this.get_secondary_unit().id;
                vals["price_unit"] = this.product.get_sec_price(this.order.pricelist, this.get_quantity()) ;
            }
        }
        else {
                let update_qty = null;
                if (data && Array.isArray(data)) {
                    let matchedData = data.find(item => item.id === this.product.id);
                    if (matchedData) {
                        update_qty = matchedData.update_qty;
                        vals["qty"] = this._initial_qty;
                        vals["secondary_qty"] = update_qty;
                        if (this.is_secondary || this.pos.config.select_uom_type == "secondary") {
                            vals["secondary_uom_id"] = this.get_secondary_unit().id;
                        }
                    }
                    else{
                        var sec_qty;
                        sec_qty = this.quantity * this.product.uom_ratio;
                        vals["secondary_qty"] = sec_qty;
                        vals["secondary_uom_id"] = this.get_secondary_unit().id;
                    }
                }
                else {
                       var sec_qty;
                       sec_qty = this.quantity * this.product.uom_ratio;
                       vals["secondary_qty"] = sec_qty;
                       vals["secondary_uom_id"] = this.get_secondary_unit().id;
                }
                }
                if (vals["qty"] === undefined || vals["qty"] === null) {
                vals["qty"] = this.quantity || this.get_quantity() || 1;
                }

        return vals;
    },
    setManualFactor(factor_val) {
        this.manual_factor = factor_val;
        this.factor = factor_val;

        // 🔹 Trigger re-render for cart
        this.trigger('change', this);
        if (this.order && this.order.pos && this.order.pos.bus) {
            this.order.pos.bus.trigger('updateOrderline', this);
        }
    },

    getDisplayData() {
        var res = super.getDisplayData(...arguments);
        var decimals = this.pos.dp["Product Unit of Measure"]
        console.log("getDisplayData  === ", this)



        if (this.get_current_uom()) {
            const primary_uom = this.get_unit();
            const current_uom = this.get_current_uom();
            const uom_ratio = this.product.uom_ratio;
            if (current_uom.factor_inv) {
                res['unit_price'] =current_uom.factor_inv * this.get_unit_display_price();
            }

            if (current_uom === primary_uom && uom_ratio > 0) {
                let factor_val;

                if (this.manual_factor !== undefined && this.manual_factor !== null) {
                    factor_val = this.manual_factor; // manual
                }

                else {
                    factor_val = this.quantity / uom_ratio; // auto
                }

                res['factor'] = formatFloat(factor_val, {
                            digits: [69, 3]})
            }

            else {
                res['factor'] = "";
            }

            //res['secondary_unit_price'] = this.product.get_sec_price(this.order.pricelist, this.get_quantity());
            res['display_secondary_receipt_changes'] = this.pos.config.display_uom_in_receipt && this.order.finalized;
            res['display_secondary_cart'] = !this.order.finalized;
            res['secondary_unit_name'] = this.get_current_uom().name;
            res['get_current_uom'] = this.get_current_uom().name;
            res['product_id'] = this.product.id;
//            res['factor'] = formatFloat(this.product.factor, {
//                            digits: [69, decimals],
//            });
            res['sec_uom'] = this.product.secondary_uom;
            res['piece_weight'] = this.product.uom_ratio
            res['product_kgs'] = this.quantity
            res['secondary'] = this.product.is_secondary_unit
        }


        res["get_quantity_str"] = this.get_quantity_str();
         res['discount'] = this.get_discount();
        return res;

    },

    set_quantity(new_qty) {
        // Call Odoo's original method so the X button & all logic still work
        const res = super.set_quantity(...arguments);

        // If quantity was changed manually, reset manual factor to auto
        if (this.manual_factor !== undefined && this.manual_factor !== null) {
            this.manual_factor = null;
            const uom_ratio = this.product.uom_ratio;
            this.factor = this.quantity / uom_ratio;
        }

        if (this.order && this.order.pos && this.order.pos.bus) {
            this.order.pos.bus.trigger('updateOrderline', this);
        }

        return res;
    }


});
