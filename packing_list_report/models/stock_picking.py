from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    vendor_address=fields.Html(string="Vendor Address")

