# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields, api


class ShPosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create(self, vals):
        vals['bill_no'] = self.env['ir.sequence'].sudo().next_by_code('pos.bill.number')
        print("vals", vals)
        res = super().create(vals)
        return res

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        # if order:
        return res

    bill_no = fields.Char(string="Bill unique no", readonly=True, store=True)



class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_info_pos(self, price, quantity, pos_config_id):
        result = super(ProductProduct, self).get_product_info_pos(price, quantity, pos_config_id)

        # Iterate over each warehouse to build the warehouse list
        warehouse_list = []
        for w in self.env['stock.warehouse'].search([]):
            # Filter stock_quant_ids for internal locations in the current warehouse
            internal_quantities = self.with_context({'warehouse': w.id}).stock_quant_ids.filtered(
                lambda q: q.location_id.usage == 'internal'
            )
            # Sum the secondary_qty for these internal quantities
            secondary_qty = sum(internal_quantities.mapped('secondary_qty'))

            # Append the warehouse information including the computed secondary_qty
            warehouse_list.append({
                'name': w.name,
                'available_quantity': self.with_context({'warehouse': w.id}).qty_available,
                'forecasted_quantity': self.with_context({'warehouse': w.id}).virtual_available,
                'uom': self.uom_name,
                'secondary_qty':  "{:.2f}".format(secondary_qty),  # Use the computed secondary_qty
                'secondary_uom':self.with_context({'warehouse': w.id}).secondary_uom.name,
            })

        # Replace the original warehouse list with the new one
        result['warehouses'] = warehouse_list

        return result

