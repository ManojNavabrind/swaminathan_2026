from odoo import fields, models, api, tools, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time

class Pricelist(models.Model):
    _inherit = "product.pricelist"
    type = fields.Selection([('retail', 'Retail'), ('wholesale', 'WholeSale'), ('export', 'Export')],
                            'Pricelist Type')



class ProductPricelist(models.Model):
    _inherit = "product.pricelist.item"

    evaluation = fields.Float(string="Evaluation")
    purchase_expense = fields.Float(string="Purchase Expense")
    expense = fields.Float(string="Expense")
    tax_id = fields.Many2one('account.tax',string='Tax')
    margin = fields.Float(string='Margin')
    packing = fields.Float(string='Packing')
    original_price = fields.Integer(string='price', compute="_compute_pricelist_value", )

    @api.depends('product_id', 'product_tmpl_id', 'categ_id')
    def _compute_pricelist_value(self):
        print('_compute_pricelist_value-----------------------')
        for item in self:
            print("item --- ", item)
            print("item --- ", item.product_id)
            print("item --- ", item.product_tmpl_id)
            print("item --- ", item.categ_id)
            price = 0.0
            product = None

            if item.product_id:
                product = item.product_id
            elif item.product_tmpl_id and item.product_tmpl_id.product_variant_id:
                product = item.product_tmpl_id.product_variant_id
            else:
                # Try to get product from context
                ctx_product_tmpl_id = self.env.context.get('default_product_tmpl_id')
                print("ctx_product_tmpl_id ---- ", ctx_product_tmpl_id)
                if ctx_product_tmpl_id:
                    product_tmpl = self.env['product.template'].browse(ctx_product_tmpl_id)
                    print('product_tmpl === ', product_tmpl)
                    if product_tmpl.exists():
                        product = product_tmpl.product_variant_id

            print('product ---- ', product)
            if product:
                current_date = datetime.now()
                currency_id = self.env.company.currency_id
                # price = product._get_tax_included_unit_price(
                #     currency=currency_id,
                #     quantity=1.0,
                #     partner=None,
                #     date=current_date
                # )

                price = item._compute_price(
                            product=product.product_tmpl_id,
                            quantity=1.0,
                            uom=product.product_tmpl_id.uom_id,
                            date=datetime.now(),
                            currency=self.env.company.currency_id,
                        )
                print("price ==========", price)
                item.original_price = round(price)
            else:
                item.original_price = 0.0

        # def _compute_pricelist_value(self):
    #     print('_compute_pricelist_value=============', self.product_tmpl_id, )
    #     current_date = datetime.now()
    #     currency_id = self.env.company.currency_id
    #     price = self._compute_price(
    #         product=self.product_tmpl_id,
    #         quantity=1.0,
    #         uom=self.product_tmpl_id.uom_id,
    #         date=current_date,
    #         currency=currency_id,
    #     )
    #
    #     print("price ----------", price)
    #     self.original_price = price

    # @api.model_create_multi
    # def create(self, vals_list):
    #     print('111111111111111111111111')
    #     records = super(ProductPricelist, self).create(vals_list)
    #     records._update_extra_price_on_product()
    #     return records
    #
    # def write(self, vals):
    #     print('2222222222222222222222222')
    #     result = super(ProductPricelist, self).write(vals)
    #     self._update_extra_price_on_product()
    #     return result
    #
    # def _update_extra_price_on_product(self):
    #     print('yyyyy')
    #     for item in self:
    #         if item.applied_on == '2_product_category' and item.categ_id:
    #             products = self.env['product.template'].search([('categ_id', '=', item.categ_id.id)])
    #     for product in products:
    #                 # Search if already exist
    #                 extra_price1 = self.env['product.pricelist.item'].search([
    #                     ('categ_id', '=', product.categ_id.id)])
    #                 print(extra_price1)
    #                 price = item.fixed_price or 0.0
    #
    #                 if not extra_price1:
    #                     # Create new Extra Price line
    #                     self.env['product.template.attribute.value'].create({
    #                         'product_tmpl_id': product.id,
    #                         'pricelist_id': item.pricelist_id.id,
    #                         'price_extra': price,
    #                     })
    #                 else:
    #                     print(extra_price1,'hhhhhhhhhhhhhhhhhhhhh')
    #                     for extra_price in extra_price1:
    #                         self.env['product.pricelist.item'].sudo().create({
    #                             'pricelist_id': extra_price.pricelist_id.id,
    #                             'applied_on':'2_product_category',
    #                             'fixed_price':extra_price.fixed_price,
    #                             'categ_id':extra_price.categ_id.id
    # ,                        })

    def _compute_price(self, product, quantity, uom, date, currency=None):
        print("V _compute_price ====", self, product, quantity, uom, date, currency)
        # for rec in self:
        if self.compute_price == 'formula':
            print('fgggggsss')
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            price = base_price
            tax = sum(self.tax_id.children_tax_ids.mapped('amount'))
            price_addtions = [self.evaluation, self.purchase_expense, self.expense, tax, self.margin, self.packing]
            price_addtions = [value for value in price_addtions if value > 0]
            for value in price_addtions:
                price += price * (value/100)
            # self.original_price = price
            # print(self.original_price,'yttttttt')
        else:
            price = super(ProductPricelist, self)._compute_price(product, quantity, uom, date, currency=None)

        return price

    # def _compute_price(self, product, quantity, uom, date, currency=None):
    #     self.ensure_one()  # Ensure only one pricelist item is processed
    #
    #     if self.compute_price == 'formula':
    #         base_price = self._compute_base_price(product, quantity, uom, date, currency)
    #         price = base_price
    #
    #         # Compute tax from children of tax_id
    #         tax = sum(self.tax_id.mapped('children_tax_ids').mapped('amount'))
    #
    #         # Add all applicable percentage-based additions
    #         price_additions = [
    #             self.evaluation,
    #             self.purchase_expense,
    #             self.expense,
    #             tax,
    #             self.margin,
    #             self.packing
    #         ]
    #         price_additions = [val for val in price_additions if val and val > 0]
    #
    #         for val in price_additions:
    #             price += price * (val / 100.0)
    #     else:
    #         price = super(ProductPricelist, self)._compute_price(product, quantity, uom, date, currency=currency)
    #
    #     return round(price, 2)

class Priceevaluation(models.Model):
    _name = "price.evaluation"
    _description = "Product Price Evaluation"


    name = fields.Char("Name", required=True)
    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    percentage = fields.Float("Adjustment (%)")
    categ_ids = fields.Many2many('product.category', string="Product Categories")
    product_variant_ids = fields.Many2many(
        'product.product',
        string="Product Variants",
        compute="_get_product_variant_ids"
    )

    @api.depends('start_date', 'end_date','categ_ids')
    def _get_product_variant_ids(self):
        for record in self:
            domain = [
                ('date_of_purchase', '>=', record.start_date),
                ('date_of_purchase', '<=', record.end_date),
            ]
            if record.categ_ids:
                domain.append(('categ_id', 'in', record.categ_ids.ids),)
            result = self.env['product.product'].sudo().search(domain)
            record.product_variant_ids = result.ids

    @api.constrains('start_date', 'end_date')
    def _check_date_overlap(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError("Start date must be before end date.")

            overlapping = self.search([
                ('id', '!=', record.id),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date),
                ('categ_ids', 'in', record.categ_ids.ids),
            ])
            if overlapping:
                raise ValidationError(
                    "Date range overlaps with another price evaluation entry: %s to %s" %
                    (overlapping[0].start_date, overlapping[0].end_date)
                )

