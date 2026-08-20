# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools
from odoo.tools import float_round
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    secondary_uom = fields.Many2one("uom.uom", string="Secondary UOM", readonly=True, store=True)
    secondary_qty = fields.Float(string="Secondary Qty", digits=(16, 0))

    # @api.depends('product_uom', 'product_uom_qty', 'secondary_qty', 'product_id')
    # def _compute_secondary_qty(self):

    #     for line in self:

    #             line.secondary_uom = line.product_uom
    #             if line.secondary_uom.category_id.name == 'Unit' and line.sell_in_unit == False:
    #                 if (line.product_id.is_secondary_unit and line.product_id.factor and line.product_id.secondary_uom) or (line.product_id.is_secondary_unit and line.product_id.secondary_uom):
    #                     line.secondary_uom = line.product_id.secondary_uom
    #                 if line.product_uom.category_id == line.secondary_uom.category_id:
    #                     line.secondary_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.secondary_uom)
    #                 else:
    #                     convert_uom_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
    #                     line.secondary_qty = convert_uom_qty * line.product_id.factor
    #             else:
    #                 if (line.product_id.is_secondary_unit and line.product_id.factor and line.product_id.secondary_uom) or (line.product_id.is_secondary_unit and line.product_id.secondary_uom):
    #                     line.secondary_uom = line.product_id.secondary_uom
    #                 if line.product_uom.category_id == line.secondary_uom.category_id:
    #                     line.secondary_qty = round(line.product_uom._compute_quantity(line.product_uom_qty, line.secondary_uom))
    #                 else:
    #                     convert_uom_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
    #                     line.secondary_qty = round(convert_uom_qty * line.product_id.factor)
    @api.onchange('product_uom_qty', 'product_id')
    def _check_piece_precision(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.uom_id.category_id.name == 'Weight':
                    # Allow up to 3 decimal places for Weight
                    rec.product_uom_qty = float("{:.3f}".format(rec.product_uom_qty))
                else:
                    # For Piece, no decimals allowed
                    print(float(rec.product_uom_qty).is_integer(),'111111111111111')
                    print(rec.product_uom_qty,'22222222222222')
                    print(float(rec.product_uom_qty),'333333333333333333')
                    print(float("{:.3f}".format(rec.product_uom_qty)),'444444444444444444')

                    if not float("{:.3f}".format(rec.product_uom_qty)).is_integer():
                        raise ValidationError("For pieces, quantity must be an integer without decimals!")
                        rec.product_uom_qty = int(rec.product_uom_qty)


    @api.onchange('product_uom_qty', 'product_id')
    def _calculate_piece(self):
        if self.product_id.uom_id.category_id.name == 'Weight':
            secondary_qty = self.product_uom_qty * self.product_id.factor
            self.secondary_qty = float_round(secondary_qty, precision_rounding=2, rounding_method="HALF-UP")

        else:
            self.secondary_qty = self.product_uom_qty

    @api.onchange('product_id')
    def _calculate_product_price(self):
        pricelist_items = self.order_id.pricelist_id.item_ids
        product_based = pricelist_items.filtered(
            lambda i: i.applied_on == '1_product' and i.product_tmpl_id.id == self.product_template_id.id)
        category_based = pricelist_items.filtered(
            lambda i: i.applied_on == '2_product_category' and i.categ_id.id == self.product_template_id.categ_id.id)
        all_product = pricelist_items.filtered(lambda i: i.applied_on == '3_global')

        pricelist_item = product_based if product_based else category_based if category_based else all_product

        if pricelist_item:
            pricelist_item = pricelist_item[0]
            price = self.product_id.standard_price
            tax = sum(pricelist_item.tax_id.children_tax_ids.mapped('amount'))
            price_addtions = [pricelist_item.evaluation, pricelist_item.purchase_expense, pricelist_item.expense, tax,
                              pricelist_item.packing, pricelist_item.margin]

            price_addtions = [value for value in price_addtions if value > 0]
            for value in price_addtions:
                price += price * (value / 100)

            if self.sell_in_unit and self.product_id.uom_ratio > 0:
                price = price * self.product_id.uom_ratio
            if pricelist_item.price_discount:
                price = (price - (price * (pricelist_item.price_discount / 100))) or 0.0
            # if pricelist_item.price_round:
            #     price = tools.float_round(price, precision_rounding=pricelist_item.price_round)
            if pricelist_item.price_surcharge:
                price += pricelist_item.price_surcharge
            self.price_unit = price
            self.cost_price = self.product_id.standard_price
            self.evaluation = pricelist_item.evaluation
            self.purchase_expense = pricelist_item.purchase_expense
            self.expenditure = pricelist_item.expense
            self.packing = pricelist_item.packing
            self.profit_margin = pricelist_item.margin

            self.order_id.amount_total = float_round(self.order_id.amount_total, precision_rounding=1,
                                                     rounding_method="UP")

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        res = super()._compute_price_unit()
        for rec in self:
            if not rec.product_id:
                continue
            if rec.pricelist_id.id != rec.order_id.pricelist_id.id:
                rec.pricelist_id = rec.order_id.pricelist_id.id
                rec.purchase_expense = rec.pricelist_item_id.purchase_expense
                rec.expenditure = rec.pricelist_item_id.expense
                rec.packing = rec.pricelist_item_id.packing
                rec.profit_margin = rec.pricelist_item_id.margin
            rec._onchange_recalculate()
        return res


    @api.onchange('profit_margin', 'expenditure', 'purchase_expense', 'evaluation', 'sell_in_unit')
    def _onchange_recalculate(self):
        print('mmmmmmmmmmmmmmmmmmmmmmm')
        pricelist_items = self.order_id.pricelist_id.item_ids
        for rec in self:
            product_based = pricelist_items.filtered(
                lambda i: i.applied_on == '1_product' and i.product_tmpl_id.id == rec.product_template_id.id)
            category_based = pricelist_items.filtered(
                lambda i: i.applied_on == '2_product_category' and i.categ_id.id == rec.product_template_id.categ_id.id)
            all_product = pricelist_items.filtered(lambda i: i.applied_on == '3_global')
            pricelist_item = product_based if product_based else category_based if category_based else all_product
            if pricelist_item:
                price = rec.product_id.standard_price
                tax = sum(pricelist_item.tax_id.children_tax_ids.mapped('amount'))
                # tax?
                price_addtions = [rec.evaluation, rec.purchase_expense, rec.expenditure, tax, rec.packing,
                                  rec.profit_margin]

                price_addtions = [value for value in price_addtions if value > 0]
                for value in price_addtions:
                    price += price * (value / 100)

                if rec.sell_in_unit and rec.product_id.uom_ratio > 0:
                    price = price * rec.product_id.uom_ratio

                if pricelist_item.price_discount:
                    price = (price - (price * (pricelist_item.price_discount / 100))) or 0.0
                # if pricelist_item.price_round:
                #     price = tools.float_round(price, precision_rounding=pricelist_item.price_round)
                if pricelist_item.price_surcharge:
                    price += pricelist_item.price_surcharge


                # ADD THIS BEFORE rec.price_unit = price:
                company_currency = rec.company_id.currency_id  # INR
                order_currency = rec.order_id.currency_id  # SGD

                if company_currency != order_currency:
                    price = company_currency._convert(
                        price,
                        order_currency,
                        rec.company_id,
                        rec.order_id.date_order or fields.Date.today()
                    )

                # existing line stays:
                rec.price_unit = price
                # rec.price_unit = price

                rec.order_id.amount_total = float_round(rec.order_id.amount_total, precision_rounding=1,
                                                        rounding_method="UP")

    # @api.onchange('sell_in_unit')
    # def _onchange_uom_qty(self):
    #     if self.sell_in_unit:
    #         self.price_subtotal = self.price_unit * self.secondary_qty
    #     else:
    #         self.price_subtotal = self.price_unit * self.product_uom_qty

    @api.onchange('sell_in_unit')
    def _onchange_uom_qty(self):
        for rec in self:
            if rec.sell_in_unit:
                rec.price_subtotal = rec.price_unit * rec.secondary_qty
            else:
                rec.price_subtotal = rec.price_unit * rec.product_uom_qty


    # @api.onchange('sell_in_unit', 'secondary_qty')
    # def _onchange_uom_qty(self):
    #     for rec in self:
    #
    #         print("========== LINE DEBUG START ==========")
    #         print(f"Product: {rec.product_id.name}")
    #         print(f"Qty: {rec.product_uom_qty}")
    #         print(f"Secondary Qty: {rec.secondary_qty}")
    #         print(f"Sell in Unit: {rec.sell_in_unit}")
    #         print(f"Price Unit (before): {rec.price_unit}")
    #
    #         if rec.sell_in_unit and rec.secondary_qty:
    #             amount = rec.price_unit * rec.product_uom_qty
    #             rec.price_unit = amount / rec.secondary_qty
    #
    #             print(f"Computed Amount: {amount}")
    #             print(f"New Price Unit: {rec.price_unit}")
    #
    #         print("========== LINE DEBUG END ==========\n")






    def _prepare_procurement_values(self, group_id=False):

        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res.update({'secondary_uom': self.secondary_uom, 'secondary_qty': self.secondary_qty})
        return res
