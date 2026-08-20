# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    secondary_uom = fields.Many2one("uom.uom", string="Secondary UOM")
    is_secondary_unit = fields.Boolean(string="Is Secondary Unit?")
    factor = fields.Float(string="Ratio")
    uom_match = fields.Boolean()
    uom_ratio = fields.Float(string='UOM Ratio',digits=(16,3))
    # location_ids = fields.Many2one('stock.location', string='Locations')
    location_ids = fields.Many2many('stock.location',string='Locations',compute='_compute_locations')

    @api.onchange('uom_ratio')
    def uom_ratio_onchange(self):
        if self.uom_id.name == 'Kg':
            self.factor = 1 / (self.uom_ratio)
        else:
            self.factor = self.uom_ratio

    @api.onchange("secondary_uom", "uom_id", "is_secondary_unit")
    def onchange_uom(self):
        self.uom_match = self.is_secondary_unit and self.secondary_uom.category_id == self.uom_id.category_id
        if not self.is_secondary_unit:
            self.secondary_uom = False
            self.factor = 0


    def update_ratio(self):
        prod = self.env['product.template'].sudo().search([])
        for rec in prod:
            if rec.uom_ratio:
                if rec.uom_id.name == 'Kg':
                    rec.factor = 1 / (rec.uom_ratio)
                else:
                    rec.factor = rec.uom_ratio

    @api.depends('product_variant_ids')
    def _compute_locations(self):
        for product in self:
            # Get all variants of the template
            variants = product.product_variant_ids.ids
            # Find quants for those variants
            quants = self.env['stock.quant'].search([
                ('product_id', 'in', variants),
                ("on_hand", "=", True),("location_id.usage", "=", "internal")
            ])
            print(quants,'quantssssssssssss')
            # Get unique location records
            locations = quants.mapped('location_id')
            product.location_ids = locations
            print(locations,'locationsssssssss')
