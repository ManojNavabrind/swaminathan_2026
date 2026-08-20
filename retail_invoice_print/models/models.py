from odoo import api, fields, models
from odoo.exceptions import UserError
from logging import getLogger


class AccountMove(models.Model):

    _inherit='account.move'

    def print_retail_invoice(self):
        print('aaaaaaaaaaaaaaaaa')
        return self.env.ref('retail_invoice_print.retail_invoice_report_pdf').report_action(self)