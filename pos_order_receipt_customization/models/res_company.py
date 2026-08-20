from odoo import models, fields
class CompanyFieldAdded(models.Model):
    _inherit = "res.company"

    phone2 = fields.Char(string="Phone 2")
    phone3 = fields.Char(string="Phone 3")