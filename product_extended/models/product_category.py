from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = "product.category"

    main_category_id = fields.Many2one('product.category', string='Main Category')