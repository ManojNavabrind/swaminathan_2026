from odoo import _, api, fields, models
from odoo.exceptions import UserError
from collections import defaultdict
import math

LABELS_PER_PAGE = 5  # 5 columns x 1 row, matches the 108mm x 20mm paper format


def _chunk(items, size):
    """Split items into chunks of given size. Returns empty list if items is empty."""
    if not items:
        return []
    return [items[i:i + size] for i in range(0, len(items), size)]


def _prepare_data(env, docids, data):
    layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))

    if data.get('active_model') == 'product.template':
        Product = env['product.template'].with_context(display_default_code=False)
    elif data.get('active_model') == 'product.product':
        Product = env['product.product'].with_context(display_default_code=False)
    elif data.get("studio") and docids:
        products = env['product.template'].with_context(display_default_code=False).browse(docids)
        quantity_by_product = defaultdict(list)
        labels_flat = []
        for product in products:
            quantity_by_product[product].append((product.barcode, 1))
            labels_flat.append((product, product.barcode))

        label_pages = _chunk(labels_flat, LABELS_PER_PAGE)
        return {
            'quantity': quantity_by_product,
            'label_pages': label_pages,
            'page_numbers': len(label_pages),
            'pricelist': layout_wizard.pricelist_id,
        }
    else:
        raise UserError(_('Product model not defined, Please contact your administrator.'))

    if not layout_wizard:
        return {}

    total = 0
    qty_by_product_in = data.get('quantity_by_product')
    products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')
    quantity_by_product = defaultdict(list)
    for product in products:
        q = qty_by_product_in[str(product.id)]
        quantity_by_product[product].append((product.barcode, q))
        total += q

    if data.get('custom_barcodes'):
        for product, barcodes_qtys in data.get('custom_barcodes').items():
            quantity_by_product[Product.browse(int(product))] += barcodes_qtys
            total += sum(qty for _, qty in barcodes_qtys)

    # flatten -> one (product, barcode) entry per physical label to print
    labels_flat = []
    for product, barcode_qty_list in quantity_by_product.items():
        for barcode, qty in barcode_qty_list:
            labels_flat.extend([(product, barcode)] * int(qty))

    label_pages = _chunk(labels_flat, LABELS_PER_PAGE)

    for i, page in enumerate(label_pages, start=1):
        print(f"Page {i}: {len(page)} labels")

    print("=" * 60)

    return {
        'quantity': quantity_by_product,
        'label_pages': label_pages,
        'total': math.ceil(total / LABELS_PER_PAGE) if total else 0,
        'page_numbers': len(label_pages),
        'price_included': data.get('price_included'),
        'extra_html': layout_wizard.extra_html,
        'pricelist': layout_wizard.pricelist_id,
    }


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection([
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('5x6', '5 x 6'),
        ('4x12xprice', '4 x 12 with price')], string="Format", default='2x7xprice', required=True)

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if '5x6' in self.print_format:
            # FIX: point at the ir.actions.report record, not the qweb template
            xml_id = 'barcode_label.report_product_template_label_5x6_noprice'

        if self.product_tmpl_ids:
            products = self.product_tmpl_ids.ids
            active_model = 'product.template'
        elif self.product_ids:
            products = self.product_ids.ids
            active_model = 'product.product'
        else:
            raise UserError(
                _("No product to print, if the product is archived please unarchive it before printing its label."))

        data = {
            'active_model': active_model,
            'quantity_by_product': {p: self.custom_quantity for p in products},
            'layout_wizard': self.id,
            'price_included': 'xprice' in self.print_format,
        }
        return xml_id, data


class ReportProductTemplateLabel5x6(models.AbstractModel):
    _name = 'report.barcode_label.report_producttemplatelabel5x6'
    _description = 'Product Label Report 5x6'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)





# from odoo import _, api, fields, models
# from odoo.exceptions import UserError
# from collections import defaultdict
# import math
#
# LABELS_PER_PAGE = 5  # 5 columns x 1 row, matches the 108mm x 20mm paper format
#
#
# def _chunk(items, size):
#     return [items[i:i + size] for i in range(0, len(items), size)] or [[]]
#
#
# def _prepare_data(env, docids, data):
#     layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))
#
#     if data.get('active_model') == 'product.template':
#         Product = env['product.template'].with_context(display_default_code=False)
#     elif data.get('active_model') == 'product.product':
#         Product = env['product.product'].with_context(display_default_code=False)
#     elif data.get("studio") and docids:
#         products = env['product.template'].with_context(display_default_code=False).browse(docids)
#         quantity_by_product = defaultdict(list)
#         labels_flat = []
#         for product in products:
#             quantity_by_product[product].append((product.barcode, 1))
#             labels_flat.append((product, product.barcode))
#         return {
#             'quantity': quantity_by_product,
#             'label_pages': _chunk(labels_flat, LABELS_PER_PAGE),
#             'page_numbers': 1,
#             'pricelist': layout_wizard.pricelist_id,
#         }
#     else:
#         raise UserError(_('Product model not defined, Please contact your administrator.'))
#
#     if not layout_wizard:
#         return {}
#
#     total = 0
#     qty_by_product_in = data.get('quantity_by_product')
#     products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')
#     quantity_by_product = defaultdict(list)
#     for product in products:
#         q = qty_by_product_in[str(product.id)]
#         quantity_by_product[product].append((product.barcode, q))
#         total += q
#
#     if data.get('custom_barcodes'):
#         for product, barcodes_qtys in data.get('custom_barcodes').items():
#             quantity_by_product[Product.browse(int(product))] += barcodes_qtys
#             total += sum(qty for _, qty in barcodes_qtys)
#
#     # flatten -> one (product, barcode) entry per physical label to print
#     labels_flat = []
#     for product, barcode_qty_list in quantity_by_product.items():
#         for barcode, qty in barcode_qty_list:
#             labels_flat.extend([(product, barcode)] * int(qty))
#
#     label_pages = _chunk(labels_flat, LABELS_PER_PAGE)
#     print("=" * 60)
#     print("Total labels :", len(labels_flat))
#     print("Total pages  :", len(label_pages))
#
#     for i, page in enumerate(label_pages, start=1):
#         print(f"Page {i}: {len(page)} labels")
#
#     print("=" * 60)
#
#     return {
#         'quantity': quantity_by_product,
#         'label_pages': label_pages,
#         'total': math.ceil(total / LABELS_PER_PAGE) if total else 0,
#         'page_numbers': len(label_pages),
#         'price_included': data.get('price_included'),
#         'extra_html': layout_wizard.extra_html,
#         'pricelist': layout_wizard.pricelist_id,
#     }
#
#
# class ProductLabelLayout(models.TransientModel):
#     _inherit = 'product.label.layout'
#
#     print_format = fields.Selection([
#         ('dymo', 'Dymo'),
#         ('2x7xprice', '2 x 7 with price'),
#         ('4x7xprice', '4 x 7 with price'),
#         ('4x12', '4 x 12'),
#         ('5x6', '5 x 6'),
#         ('4x12xprice', '4 x 12 with price')], string="Format", default='2x7xprice', required=True)
#
#     def _prepare_report_data(self):
#         xml_id, data = super()._prepare_report_data()
#
#         if '5x6' in self.print_format:
#             # FIX: point at the ir.actions.report record, not the qweb template
#             xml_id = 'barcode_label.report_product_template_label_5x6_noprice'
#
#         if self.product_tmpl_ids:
#             products = self.product_tmpl_ids.ids
#             active_model = 'product.template'
#         elif self.product_ids:
#             products = self.product_ids.ids
#             active_model = 'product.product'
#         else:
#             raise UserError(
#                 _("No product to print, if the product is archived please unarchive it before printing its label."))
#
#         data = {
#             'active_model': active_model,
#             'quantity_by_product': {p: self.custom_quantity for p in products},
#             'layout_wizard': self.id,
#             'price_included': 'xprice' in self.print_format,
#         }
#         return xml_id, data
#
#     # def _prepare_report_data(self):
#     #     xml_id, data = super()._prepare_report_data()
#     #
#     #     if '5x6' in self.print_format:
#     #         # FIX: point directly at the template we defined, no dynamic guessing
#     #         xml_id = 'barcode_label.report_producttemplatelabel5x6'
#     #
#     #     if self.product_tmpl_ids:
#     #         products = self.product_tmpl_ids.ids
#     #         active_model = 'product.template'
#     #     elif self.product_ids:
#     #         products = self.product_ids.ids
#     #         active_model = 'product.product'
#     #     else:
#     #         raise UserError(_("No product to print, if the product is archived please unarchive it before printing its label."))
#     #
#     #     data = {
#     #         'active_model': active_model,
#     #         'quantity_by_product': {p: self.custom_quantity for p in products},
#     #         'layout_wizard': self.id,
#     #         'price_included': 'xprice' in self.print_format,
#     #     }
#     #     return xml_id, data
#
#
# class ReportProductTemplateLabel5x6(models.AbstractModel):
#     _name = 'report.barcode_label.report_producttemplatelabel5x6'
#     _description = 'Product Label Report 5x6'
#
#     def _get_report_values(self, docids, data):
#         return _prepare_data(self.env, docids, data)
# # from odoo import _, api, fields, models
# # from odoo.exceptions import UserError
# # from collections import defaultdict
# # import math
# # import pprint
# #
# # def _prepare_data(env, docids, data):
# #     # change product ids by actual product object to get access to fields in xml template
# #     # we needed to pass ids because reports only accepts native python types (int, float, strings, ...)
# #
# #     layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))
# #     if data.get('active_model') == 'product.template':
# #         Product = env['product.template'].with_context(display_default_code=False)
# #     elif data.get('active_model') == 'product.product':
# #         Product = env['product.product'].with_context(display_default_code=False)
# #     elif data.get("studio") and docids:
# #         # special case: users trying to customize labels
# #         products = env['product.template'].with_context(display_default_code=False).browse(docids)
# #         quantity_by_product = defaultdict(list)
# #         for product in products:
# #             quantity_by_product[product].append((product.barcode, 1))
# #         return {
# #             'quantity': quantity_by_product,
# #             'page_numbers': 1,
# #             'pricelist': layout_wizard.pricelist_id,
# #         }
# #     else:
# #         raise UserError(_('Product model not defined, Please contact your administrator.'))
# #
# #     if not layout_wizard:
# #         return {}
# #
# #     total = 0
# #     qty_by_product_in = data.get('quantity_by_product')
# #     # search for products all at once, ordered by name desc since popitem() used in xml to print the labels
# #     # is LIFO, which results in ordering by product name in the report
# #     products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')
# #     quantity_by_product = defaultdict(list)
# #     for product in products:
# #         q = qty_by_product_in[str(product.id)]
# #         quantity_by_product[product].append((product.barcode, q))
# #         total += q
# #     if data.get('custom_barcodes'):
# #         # we expect custom barcodes format as: {product: [(barcode, qty_of_barcode)]}
# #         for product, barcodes_qtys in data.get('custom_barcodes').items():
# #             quantity_by_product[Product.browse(int(product))] += (barcodes_qtys)
# #             total += sum(qty for _, qty in barcodes_qtys)
# #     page_number1=(total - 1) // (layout_wizard.rows * layout_wizard.columns)+1
# #     print("=" * 80)
# #     print("TOTAL:", total)
# #     print("QUANTITY:")
# #     pprint.pprint(quantity_by_product)
# #     print("=" * 80)
# #     print("PAGE_NUMBERS:",page_number1)
# #
# #     return {
# #         'quantity': quantity_by_product,
# #         'total': math.ceil(total / 5),
# #         'page_numbers': (total - 1) // (layout_wizard.rows * layout_wizard.columns)+1,
# #         'price_included': data.get('price_included'),
# #         'extra_html': layout_wizard.extra_html,
# #         'pricelist': layout_wizard.pricelist_id,
# #     }
# #
# # class ProductLabelLayout(models.TransientModel):
# #     _inherit = 'product.label.layout'
# #
# #
# #     print_format = fields.Selection([
# #         ('dymo', 'Dymo'),
# #         ('2x7xprice', '2 x 7 with price'),
# #         ('4x7xprice', '4 x 7 with price'),
# #         ('4x12', '4 x 12'),
# #         ('5x6', '5 x 6'),
# #         ('4x12xprice', '4 x 12 with price')], string="Format", default='2x7xprice', required=True)
# #
# #     def _prepare_report_data(self):
# #         xml_id,data = super()._prepare_report_data()
# #         if '5x6' in self.print_format:
# #             xml_id = 'barcode_label.report_product_template_label_%sx%s' % (self.columns, self.rows)
# #             if 'xprice' not in self.print_format:
# #                 xml_id += '_noprice'
# #         if self.product_tmpl_ids:
# #             products = self.product_tmpl_ids.ids
# #             active_model = 'product.template'
# #         elif self.product_ids:
# #             products = self.product_ids.ids
# #             active_model = 'product.product'
# #         else:
# #             raise UserError(_("No product to print, if the product is archived please unarchive it before printing its label."))
# #
# #         # Build data to pass to the report
# #         data = {
# #             'active_model': active_model,
# #             'quantity_by_product': {p: self.custom_quantity for p in products},
# #             'layout_wizard': self.id,
# #             'price_included': 'xprice' in self.print_format,
# #         }
# #         print("=========XML REPORT =======", xml_id)
# #         return xml_id, data
# #
# #
# #
# # class ReportProductTemplateLabel5x6(models.AbstractModel):
# #     _name = 'report.barcode_label.report_producttemplatelabel5x6'
# #     _description = 'Product Label Report 5x6'
# #
# #     def _get_report_values(self, docids, data):
# #         pprint.pprint(data)
# #         print(">>> REPORT CALLED <<<")
# #         return _prepare_data(self.env, docids, data)
# #     # def _get_report_values(self, docids, data):
# #     #     raise UserError("MY CUSTOM REPORT IS RUNNING")
