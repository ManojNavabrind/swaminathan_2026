from odoo import api, fields, models,tools,_
from odoo.exceptions import UserError
from logging import getLogger
from datetime import date

logger = getLogger(__name__)

class ProductProduct(models.Model):
    _inherit='product.product'

    # evaluation = fields.Float(string="Evaluation", digits=[2,1])
    # expenditure = fields.Float(string="Expenditure", default=10,digits=[2,1])
    # profit_margin = fields.Float(string='Profit Margin', digits=[2,1])
    evaluation_id = fields.Float('Evaluation', related='product_tmpl_id.evaluation_id')
    # def _compute_evaluation_percentage(self):
    #     print('_compute_evaluation_percentage ===================')
    #     for rec in self:
    #         evaluation = self.env['price.evaluation'].search([('start_date', '<=', rec.date_of_purchase),
    #                                                       ('end_date', '>=', rec.date_of_purchase)])
    #         rec.evaluation_id = evaluation.id
    @api.onchange('evaluation','expenditure','profit_margin','standard_price')
    def variant_cost_calculation(self):
        for product_id in self:
            if product_id:
                pr = product_id._origin
                prod = product_id._origin.id
                extra_price = self.env['product.pricelist.item'].search([('product_id', '=', prod)])

                cal = product_id.standard_price
                evaluation = product_id.evaluation
                expenditure = product_id.expenditure
                profit_margin = product_id.profit_margin

                cal1 = cal * (evaluation / 100)
                cal = cal + cal1

                cal2 = cal * (expenditure/100)
                cal = cal + cal2

                cal3 = cal * (profit_margin/100)
                cal = cal + cal3


                sec_cost = product_id.secondary_cost_price

                sec_cal1 = sec_cost * (evaluation / 100)
                sec_cost = sec_cost + sec_cal1

                sec_cal2 = sec_cost * (expenditure / 100)
                sec_cost = sec_cost + sec_cal2

                sec_cal3 = sec_cost * (profit_margin / 100)
                sec_cost = sec_cost + sec_cal3


                if extra_price:
                    extra_price.fixed_price = cal
                else:
                        print('yyyyyyyyy')
                        self.env['product.pricelist.item'].create({
                            'product_id': product_id.id,
                            'fixed_price': cal,
                            'min_quantity': 1,
                            'product_tmpl_id': product_id.product_tmpl_id.id,
                            'applied_on': '0_product_variant'
                        })
                product_id.lst_price = cal
                product_id.secondary_sale_price = sec_cost
            else:
                product_id.standard_price = 0

class ProductTemplate(models.Model):
    _inherit = "product.template"

    evaluation_id = fields.Float('Price Evaluation', compute='_compute_evaluation_percentage')

    def _compute_evaluation_percentage(self):
        print('_compute_evaluation_percentage ===================')
        for rec in self:
            evaluation = self.env['price.evaluation'].search([('start_date', '<=', rec.date_of_purchase),
                                                          ('end_date', '>=', rec.date_of_purchase),('categ_ids', '=', rec.categ_id.id)])
            print('evaluation ===================', evaluation)
            rec.evaluation_id = evaluation.percentage

    def _compute_item_count(self):
        for template in self:
            # Pricelist item count counts the rules applicable on current template or on its variants.
            template.pricelist_item_count = template.env['product.pricelist.item'].search_count([
                '&',
                '|','|', ('product_tmpl_id', '=', template.id), ('product_id', 'in', template.product_variant_ids.ids),('categ_id','=',template.categ_id.id),
                ('pricelist_id.active', '=', True),
            ])

    def open_pricelist_rules(self):
        self.ensure_one()
        domain = ['|', '|',
                  ('product_tmpl_id', '=', self.id),
                  ('product_id', 'in', self.product_variant_ids.ids),
                  ('categ_id', '=', self.categ_id.id)]
        return {
            'name': _('Price Rules'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('product.product_pricelist_item_tree_view_from_product').id, 'tree'),
                      (False, 'form')],
            'res_model': 'product.pricelist.item',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context': {
                'default_product_tmpl_id': self.id,
                'default_applied_on': '1_product',
                'product_without_variants': self.product_variant_count == 1,
                'search_default_visible': True,
            },
        }

    purchase_cost = fields.Float(string='Purchase Cost',default=1)
    evaluation = fields.Float(string="Evaluation",digits=[2,1])
    appreciation = fields.Float(string="Appreciation",digits=[2,1])
    expenditure = fields.Float(string="Expenditure", digits=[2,1])
    profit_margin = fields.Float(string='Profit Margin',digits=[2,1])
    secondary_cost_price = fields.Float(string='Secondary UOM Cost price',digits='Product Price')
    secondary_sale_price = fields.Float(string='Secondary UOM Sale price',digits='Product Price')
    date_of_purchase = fields.Date(string='Date of Purchase')
    length = fields.Float(string='Length')
    width = fields.Float(string='Width')
    height = fields.Float(string='Height')

    @api.onchange('length','width','height')
    def compute_volume(self):
        volume_in = self.length * self.width * self.height
        self.volume = volume_in * 0.000016387064

    def update_cost_price(self):
        rec = self.env['product.template'].sudo().search([])
        for product_id in rec:
            if product_id:

                cal = product_id.standard_price
                evaluation = product_id.evaluation
                expenditure = product_id.expenditure
                profit_margin = product_id.profit_margin

                cal1 = cal * (evaluation / 100)
                cal = cal + cal1

                cal2 = cal * (expenditure/100)
                cal = cal + cal2

                cal3 = cal * (profit_margin/100)
                cal = cal + cal3

                product_id.list_price = cal

                prod_tmpl = self.env['product.template'].browse(product_id.id)
                on_hand = self.env['stock.quant'].search(
                    [('location_id.usage', '=', 'internal'), ('product_id', '=', product_id.product_variant_id.id)])
                qty = 0
                sec_qty1 = 0
                if on_hand:
                    for rec in on_hand:
                        qty = qty + rec.quantity
                        sec_qty1 = sec_qty1 + rec.secondary_qty
                    if qty:
                        ratio = prod_tmpl.factor
                        sec_qty = sec_qty1
                        sec_cost = (qty / sec_qty) * prod_tmpl.standard_price
                        prod_tmpl.secondary_cost_price = sec_cost
                        evaluation = prod_tmpl.evaluation
                        expenditure = prod_tmpl.expenditure
                        profit_margin = prod_tmpl.profit_margin
                        cal = sec_cost
                        cal1 = cal * (evaluation / 100)
                        cal = cal + cal1
                        cal2 = cal * (expenditure / 100)
                        cal = cal + cal2
                        cal3 = cal * (profit_margin / 100)
                        cal = cal + cal3
                        prod_tmpl.secondary_sale_price = cal

            else:
                product_id.standard_price = 0


    @api.onchange('evaluation','expenditure','profit_margin','standard_price')
    def cost_calculation(self):
        for product_id in self:
            if product_id:

                cal = product_id.standard_price
                evaluation = product_id.evaluation
                expenditure = product_id.expenditure
                profit_margin = product_id.profit_margin

                cal1 = cal * (evaluation / 100)
                cal = cal + cal1

                cal2 = cal * (expenditure/100)
                cal = cal + cal2

                cal3 = cal * (profit_margin/100)
                cal = cal + cal3

                sec_cost = product_id.secondary_cost_price

                sec_cal1 = sec_cost * (evaluation / 100)
                sec_cost = sec_cost + sec_cal1

                sec_cal2 = sec_cost * (expenditure / 100)
                sec_cost = sec_cost + sec_cal2

                sec_cal3 = sec_cost * (profit_margin / 100)
                sec_cost = sec_cost + sec_cal3

                product_id.list_price = cal
                product_id.secondary_sale_price = sec_cost

            else:
                product_id.standard_price = 0

    

        

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def scrap_wizard(self):
        product_ids = []
        for rec in self:
            if rec.move_ids:
                for products in rec.move_ids:
                    product_ids.append(products.product_id.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap',
            'res_model': 'stock.scrap',
            'view_mode': 'form',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
                'product_ids':product_ids,
            },
        }

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.picking_type_id.code == 'incoming':
            purchase = self.purchase_id
            for  rec in purchase:
                if rec.order_line:
                    for rec1 in  rec.order_line:
                        product_id = self.env['product.template'].browse(rec1.product_id.product_tmpl_id.id)
                        if rec1.product_uom != product_id.uom_id:
                            purchase_qty = rec1.product_qty
                            purchase_unit = rec1.price_unit
                            for rec in self.move_ids:
                                   if rec.purchase_line_id.id == rec1.id:
                                       received_qty = rec.quantity
                            unit_weight = purchase_qty/ received_qty
                            cost_price = unit_weight * purchase_unit
                            if product_id.standard_price < cost_price:
                                product_id.standard_price = cost_price
                                cal = cost_price
                                evaluation = product_id.evaluation
                                expenditure = product_id.expenditure
                                profit_margin = product_id.profit_margin

                                cal1 = cal * (evaluation / 100)
                                cal = cal + cal1

                                cal2 = cal * (expenditure / 100)
                                cal = cal + cal2

                                cal3 = cal * (profit_margin / 100)
                                cal = cal + cal3
                                product_id.list_price = cal
                        if product_id.is_secondary_unit:
                                prod_tmpl = self.env['product.template'].browse(rec1.product_id.product_tmpl_id.id)
                                on_hand = self.env['stock.quant'].search(
                                    [('location_id.usage', '=', 'internal'), ('product_id', '=', rec1.product_id.id)])
                                qty = 0
                                sec_qty1 = 0
                                if on_hand:

                                    for rec in on_hand:
                                        qty = qty+rec.quantity
                                        sec_qty1 = sec_qty1+rec.secondary_qty
                                    ratio = prod_tmpl.factor
                                    sec_qty = sec_qty1
                                    sec_cost = (qty / sec_qty) * prod_tmpl.standard_price
                                    prod_tmpl.secondary_cost_price = sec_cost
                                    evaluation = prod_tmpl.evaluation
                                    expenditure = prod_tmpl.expenditure
                                    profit_margin = prod_tmpl.profit_margin
                                    cal = sec_cost
                                    cal1 = cal * (evaluation / 100)
                                    cal = cal + cal1
                                    cal2 = cal * (expenditure / 100)
                                    cal = cal + cal2
                                    cal3 = cal * (profit_margin / 100)
                                    cal = cal + cal3
                                    prod_tmpl.secondary_sale_price = cal
        return res


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    manual_purchase_date = fields.Date(string="Manual Purchase Date")

    # @api.model
    # def create(self, vals):
    #     purchase_order = super(PurchaseOrder, self).create(vals)
    #     self.env['product.template'].latest_cost_price(purchase_order)
    #     return purchase_order

    def button_confirm(self):

        res = super(PurchaseOrder,self).button_confirm()

        for line in self.order_line:
            line.product_id.standard_price = line.price_unit
            # line.product_id.date_of_purchase = self.date_approve.date()
            line.product_id.product_tmpl_id.date_of_purchase = self.manual_purchase_date

        return res




    def latest_cost_price(self):
        for order in self.search([('state','=','purchase')],order="id ASC"):
            for line in order.order_line:
                line.product_id.standard_price = line.price_unit
                # line.product_id.date_of_purchase = order.date_approve.date()
                line.product_id.date_of_purchase = self.manual_purchase_date
                line.product_id.date_of_purchase = order.manual_purchase_date


class PackageType(models.Model):
    _inherit = 'stock.package.type'

    base_weight = fields.Float(string='Weight', help='Weight of the package type', digits='Stock Weight')
    max_weight = fields.Float('Max Weight', help='Maximum weight shippable in this packaging', digits='Stock Weight')
