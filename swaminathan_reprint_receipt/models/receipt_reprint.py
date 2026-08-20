import logging
import base64
# import xlsxwriter
from io import StringIO
from odoo import api, fields, models,_
from datetime import datetime, date
import re
import ast
_logger = logging.getLogger(__name__)


class POSORDERRECEIPT(models.Model):
    _inherit = 'pos.order'

    def is_refund_order(self):
        self.ensure_one()
        for line in self.lines:
            if line.qty < 0:
                return True
        return False

    def get_bill_type(self):
        self.ensure_one()
        return "REFUND BILL" if self.is_refund_order() else "CASH BILL"

    def get_pdf_print(self):
        result = []
        for line in self.lines:
            # Check if 'factor' exists on the line to avoid errors
            factor_val = getattr(line, 'factor', 0)

            result.append({
                'product_name': line.product_id.display_name,
                'barcode': line.product_id.barcode,
                'qty': line.qty,  # This is usually the weight in KG
                'factor': factor_val,  # This is your PIECES count
                'uom': line.product_uom_id.name,  # Needed for the IF logic in XML
                'discount': line.discount or 0.0,
                'weight': line.product_id.weight or 0.0,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'price_subtotal_incl': line.price_subtotal_incl,
                'tax': line.price_subtotal_incl - line.price_subtotal,
                'secondary_qty':line.product_id.uom_ratio,
            })
        return result


    def get_mode(self):
        self.env.cr.execute("""
            SELECT
                ppm.name::text,
                pp.amount
            FROM
                pos_payment pp
                JOIN pos_payment_method ppm ON (ppm.id = pp.payment_method_id)
            WHERE
                pp.pos_order_id = %d
        """ % (
            self.id))
        mode = [i for i in self.env.cr.dictfetchall()]

        lang = self.env.lang
        updated_vals = []

        for val in mode:
            product_name = val['name']
            pattern = r'\((.*?)\)'
            match = re.search(pattern, product_name)
            val_str = match.group(1) if match else False
            product_name = re.sub(pattern, '', product_name).strip()
            product_dict = ast.literal_eval(product_name)
            if not val_str:
                product = product_dict.get(lang, next(iter(product_dict.values())))
            else:
                product = product_dict.get(lang, next(iter(product_dict.values()))) + "(" + str(val_str) + ")"

            val['name'] = product
            updated_vals.append(val)

        return mode


class Company(models.Model):
    _inherit = "res.company"

    report_title = fields.Char(string='Company Tagline', compute='compute_report_header')

    @api.depends('report_header')
    def compute_report_header(self):
        for rec in self:
            if rec.report_header:
                cleaned_header = re.sub('<[^<]+?>', '', rec.report_header)
                rec.report_title = cleaned_header
            else:
                rec.report_title = ''
