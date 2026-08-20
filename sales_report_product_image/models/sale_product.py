# See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models
from datetime import date



class SaleOrder(models.Model):
    _inherit = "sale.order"

    print_image = fields.Boolean("Print Image", 
        help="""If ticked, you can see the product image in 
report of sale order/quotation""",default=True)
    image_sizes = fields.Selection(
        [("image", "Big sized Image"),
        ("image_medium", "Medium Sized Image"),
        ("image_small", "Small Sized Image"),
        ], "Image Sizes", default="image_small",
        help="Image size to be displayed in report")

    manual_invoice_no = fields.Char(
        string="Manual Invoice No",
        help="Enter the manual invoice number for customs/export reports"
    )

    manual_invoice_date = fields.Date(string="Manual Invoice Date",
        help="Enter the manual invoice date for customs/export reports")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_small = fields.Binary("Product Image", related="product_id.image_1920")
    barcode = fields.Char(string="Barcode", related="product_id.barcode")

    @api.onchange('product_template_id', 'date_of_purchase','product_id','product_uom_qty','price_unit')
    def _onchange_eval_and_price(self):
        PriceEvalModel = self.env['price.evaluation']
        for line in self:
            if not line.product_id:
                continue
            ref_date = (
                line.date_of_purchase
                or (line.order_id.date_order and line.order_id.date_order.date())
                or date.today()
            )
            print("Reference Date:11111111111111111111111111111111111111111", ref_date)
            price_eval_record = PriceEvalModel.search([
                ('start_date', '<=', ref_date),
                ('end_date', '>=', ref_date),
            ], order='start_date desc', limit=1)
            line.evaluation = price_eval_record.percentage if price_eval_record else 0.0

