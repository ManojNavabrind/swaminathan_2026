from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError
from logging import getLogger
from odoo.tools import float_round
import math
from odoo.tools import formatLang



class SaleOrderLine(models.Model):
    _inherit='sale.order.line'

    evaluation = fields.Float(string="Evaluation", digits=[2, 1], readonly=False)
    purchase_expense = fields.Float(string="Purchase Expense")
    packing = fields.Float(string="Packing")
    expenditure = fields.Float(string="Expenditure", digits=[2, 1], related='product_id.expenditure', readonly=False)
    profit_margin = fields.Float(string="Profit Margin", default=10, digits=[2, 1], related='product_id.profit_margin', readonly=False)
    sell_in_unit = fields.Boolean(string='Sale in Sec. UOM')
    cost_price = fields.Float(string='Cost price',related='product_id.standard_price')
    date_of_purchase = fields.Date(string='Date of Purchase',related='product_id.date_of_purchase')
    pricelist_id = fields.Many2one('product.pricelist',string="Pricelist")
    use_sec_qty = fields.Boolean(string='Use Secondary Qty')

    


class SaleOrder(models.Model):

    _inherit='sale.order'

    is_agent = fields.Boolean(string='Agent Fee')



    @api.onchange('partner_id')
    def is_agent_compute(self):

        if self.partner_id:
            if self.partner_id.country_id.code != 'IN':
                self.is_agent = True
            else:
                self.is_agent = False

    
    # @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')
    # def _compute_amounts(self):
    #     """round UP roundoff amount_total."""
    #     res = super()._compute_amounts()
    #     for order in self:
    #         order.update({'amount_total': math.ceil(order.amount_total)})

    #     return res    
    




    def agent_fee(self):
        services = self.env['product.product'].search([('detailed_type', '=', 'service')])

        if services:
            sale_order_lines = []

            # Check if the agent fee already exists in the order lines
            agent_fee_exists = any(
                line.product_id.detailed_type == 'service' and 'Export' in line.product_id.product_tag_ids.mapped(
                    'name')
                for line in self.order_line
            )

            if agent_fee_exists:
                raise UserError(_("Agent fee has already been added to this order."))

            for rec in services:
                if rec.product_tag_ids:
                    for rec1 in rec.product_tag_ids:
                        if rec1.name == 'Export':
                            sale_order_lines.append((0, 0, {
                                'product_id': rec.id,
                                'name': rec.name,
                                'product_uom_qty': 1,
                                'price_unit': rec.list_price,
                            }))

            # Only add the new sale order lines if they are not empty
            if sale_order_lines:
                self.write({'order_line': sale_order_lines})

class ResCompany(models.Model):
    _inherit = 'res.company'

    pan_no = fields.Char(string='PAN No')

class productpricelist(models.Model):
    _inherit="product.pricelist"

    note = fields.Html(string='Note')
