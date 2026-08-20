# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(
            ['sh_secondary_uom','secondary_uom','sh_is_secondary_unit','secondary_sale_price','factor','uom_ratio','evaluation_id'])
        return result

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].extend(
            ['pan_no', 'street', 'street2','logo'])
        return result

    def _loader_params_product_pricelist(self):
        result = super()._loader_params_product_pricelist()
        result['search_params']['fields'].extend(
            ['type'])
        return result

    def _product_pricelist_item_fields(self):
        return [
                'id',
                'product_tmpl_id',
                'product_id',
                'pricelist_id',
                'price_surcharge',
                'price_discount',
                'price_round',
                'price_min_margin',
                'price_max_margin',
                'company_id',
                'currency_id',
                'date_start',
                'date_end',
                'compute_price',
                'fixed_price',
                'percent_price',
                'base_pricelist_id',
                'base',
                'categ_id',
                'min_quantity',
                'evaluation',
                'expense',
                'tax_id',
                'packing',
                'margin',
                ]


