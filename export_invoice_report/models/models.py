from odoo import api, fields, models,tools
from odoo.exceptions import UserError
from logging import getLogger


logger = getLogger(__name__)

class StockPicking(models.Model):
    _inherit='stock.picking'

    country_of_origin  = fields.Many2one('res.country',string='Country of Origin of Goods')
    country_of_dest = fields.Many2one('res.country',string='Country of final Destination')
    pre_carraige = fields.Char(string='Pre-Carraige by')
    place_of_receipt = fields.Char(string='Place of Receipt')
    flight_no = fields.Char(string='Vessel / Fight No')
    port_of_loading = fields.Char(string='Port of Loading')
    port_of_discharge = fields.Char(string='Port of Discharge')
    place_of_discharge = fields.Char(string='Place of Discharge')
    container_no = fields.Char(string='Container No')
    marks_no = fields.Char(string='Marks & No.')
    no_pkgs = fields.Char(string='No of Pkgs')
    pkgs_kind = fields.Char(string='Kind of Pkgs')
    buyer_order_no = fields.Char(string='Buyer Order No')
    buyer_date = fields.Date(string='Buyer Date')
    expoter_ref = fields.Char(string='Exporter Ref')
    iec_no = fields.Char(string='IEC No')
    invoice_no = fields.Many2many('account.move',string="Invoice No.")
    total_gross = fields.Float(string='Gross',compute='gross_compute')
    other_ref = fields.Text(string='Other Ref')

    def gross_compute(self):

        packages = self.move_line_ids.mapped('result_package_id')
        wgt=0
        for package in packages:
            pack = self.move_line_ids.filtered(lambda l: l.result_package_id == package)
            total=0
            gross = 0
            for rec in pack:
                total = total+ rec.move_id.net_weight
            gross = total+package.package_type_id.base_weight
            wgt = wgt + gross
        self.total_gross = wgt


class AccountMoveLine(models.Model):
    _inherit="account.move.line"

    gross_weight = fields.Float(string='Gross Weight')

class AccountMove(models.Model):
    _inherit = "account.move"
    amount_word_in_words = fields.Char(string='Amount in Words',compute='_compute_amount_word_in_words')

    @api.depends('invoice_line_ids.price_total', 'currency_id')
    def _compute_amount_word_in_words(self):
        for rec in self:
            if rec.invoice_line_ids.filtered(lambda line: line.product_id.detailed_type):
                amount_word = sum(
                    rec.invoice_line_ids.filtered(lambda line: line.product_id.detailed_type).mapped(
                        'price_total'))
                if rec.currency_id.name == 'USD':
                    amount_word_in_words = num2words(amount_word, to='currency', lang='en_US')
                    amount_word_in_words = (
                        amount_word_in_words.replace("euro", "").replace(",", "").replace("zero cents", ""))
                    if "cents" in amount_word_in_words:
                        cents_index = amount_word_in_words.find("cents")
                        amount_part = amount_word_in_words[:cents_index]
                        cents_part = amount_word_in_words[cents_index:]
                        amount_part_words = amount_part.split()
                        amount_part_words[-1] = "Dollars and " + amount_part_words[-1]
                        amount_word_in_words = " ".join(amount_part_words) + " " + cents_part.replace(" ", "-")
                    # vals = "US Dollars" + ' ' + amount_word_in_words + " Only"
                    rec.amount_word_in_words = amount_word_in_words.upper()

                elif rec.currency_id.name == 'INR':
                    amount_word_in_words = num2words(amount_word, to='currency', lang='en_IN')
                    # Replace certain words and formatting
                    amount_word_in_words = (
                        amount_word_in_words.replace("euro", "").replace("cents", "paise").replace(",", "").replace(
                            "zero paise", ""))
                    if "paise" in amount_word_in_words:
                        paise_index = amount_word_in_words.find("paise")
                        amount_part = amount_word_in_words[:paise_index]
                        paise_part = amount_word_in_words[paise_index:]
                        amount_part_words = amount_part.split()
                        amount_part_words[-1] = "Rupees and " + amount_part_words[-1]
                        amount_word_in_words = " ".join(amount_part_words) + " " + paise_part.replace(" ", "-")
                    #vals = "Rupees " + amount_word_in_words + " Only"
                    rec.amount_word_in_words = amount_word_in_words.upper()

                else:
                    rec.amount_word_in_words = ""
            else:
                rec.amount_word_in_words = ""
