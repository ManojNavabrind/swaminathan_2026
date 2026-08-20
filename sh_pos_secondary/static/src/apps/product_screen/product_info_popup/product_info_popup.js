odoo.define('sh_pos_secondary.product_info_popup', function(require) {
    'use strict';

    const PosModel = require('point_of_sale.models');

    const _super_posmodel = PosModel.PosModel.prototype;    

    PosModel.PosModel = PosModel.PosModel.extend({
        async getProductInfo(product, quantity) {
            const result = await _super_posmodel.getProductInfo.apply(this, arguments);

            // New fields to be added
            const order = this.get_order();
            const totalQuantity = order.orderlines.reduce((total, line) => total + line.quantity, 0);
            const averagePriceWithoutTax = order.orderlines.length
                ? order.orderlines.reduce((total, line) => total + line.price_without_tax, 0) / order.orderlines.length
                : 0;
            const averagePriceWithoutTaxCurrency = this.env.utils.formatCurrency(averagePriceWithoutTax);

            // Add the new fields to the result object
            return Object.assign({}, result, {
                totalQuantity,
                averagePriceWithoutTaxCurrency,
            });
        }
    });
});
