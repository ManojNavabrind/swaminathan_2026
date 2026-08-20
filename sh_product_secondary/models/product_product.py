# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,api


class ShProductProduct(models.Model):
    _inherit = 'product.product'

    category_id = fields.Many2one(
        "uom.category",
        "UOM Category",
        related="uom_id.category_id"
    )



class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('barcode'):
                vals['barcode'] = self.env[
                    'ir.sequence'
                ].next_by_code('product.barcode')

        records = super().create(vals_list)
        return records
