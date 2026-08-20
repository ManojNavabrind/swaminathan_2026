# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Point Of Sale Secondary Unit Of Measure",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "summary": "POS Secondary,Product Secondary Unit Of Measure, Point Of Sale Secondary UOM,POS multiple uom,point of sale multiple uom, Manage Multiple POS UOM, point of sale Unit Of Measure, pos Unit Of Measure,POS Secondary Unit Of Measure Odoo",
    "description": """Do you want the secondary unit of measure in the point of sale (POS) product? Yes! So, You are at the right place, We have created a beautiful module to manage a secondary unit of measure in POS product. It will help you to get easily secondary unit value. so you don't need to waste your time to calculate that value. cheers! Point Of Sale - Secondary Unit Of Measure Odoo, POS Secondary UOM Odoo Set Secondary Unit Of Measure For POS, Provide Different POS Product UOM Module, Manage Point Of Sale Multiple Unit Of Measure, Setup Secondary Unit Of Measure In POS Goods, Double Unit Of Measure In POS, Multiple UOM For Single Product Odoo """,
    "version": "0.0.1",
    "depends": ["point_of_sale", 'sh_product_secondary','gt_secondary_uom'],
    "application": True,
    "data": ["views/pos_order.xml",
             "views/res_config_settings.xml",
             "data/cron.xml",
             # "views/res_partner_extended_view.xml",
             ],
    'assets': {'point_of_sale._assets_pos': [
        'sh_pos_secondary/static/src/apps/control_buttons/change_UOM_button/change_UOM_button.js',
        'sh_pos_secondary/static/src/apps/control_buttons/change_UOM_button/change_UOM_button.xml',
        'sh_pos_secondary/static/src/apps/control_buttons/update_price_button/update_price_button.js',
        'sh_pos_secondary/static/src/apps/control_buttons/update_price_button/price_window.js',
        'sh_pos_secondary/static/src/apps/control_buttons/update_price_button/price_window.xml',
        'sh_pos_secondary/static/src/apps/product_screen/product_info_popup/product_info_popup.xml',
        'sh_pos_secondary/static/src/overrides/models/models.js',
        'sh_pos_secondary/static/src/overrides/components/order_line/order_line.xml',
        'sh_pos_secondary/static/src/apps/customer_screen/customer_form.xml',
        ],
               },
    # 'assets':{'point_of_sale.assets':[
    #     'sh_pos_secondary/static/src/apps/customer_screen/customer_form.js',
    #     ]
    #      },
    "auto_install": False,
    "installable": True,
    "price": 50,
    "currency": "EUR",
    "license": "OPL-1",
    "images": ["static/description/background.png", ]
}
