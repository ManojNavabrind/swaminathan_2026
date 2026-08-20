# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Product Secondary Unit of Measure",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Productivity",
    "summary": "product secondary uom app set secondary unit of measure manage multiple goods uom odoo double product uom module Set Product Secondary Unit of Measure Secondary Unit of Measure in inventory management Product UoM configuration Odoo",
    "description": """
Do you have more than one unit of measure in product?
Yes! So, You are at the right palce,
We have created beautiful module to manage secondary
unit of measure in product
It will help you to get easily secondary unit value.
so you don't need to waste your time to calculate that value.
product secondary uom app, set secondary unit of measure,
manage multiple goods uom odoo, double product uom module""",

    "version": "0.0.1",
    "depends": [
                    "product",
                    "stock",
                ],
    "application": True,
    "data": [
            "data/sequence.xml",
            "security/sh_product_secondary_unit_groups.xml",
            "views/product_product_views.xml",
            "views/product_template_views.xml",
            "views/stock_quant_views.xml",
            ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": "EUR",
    "images": ['static/description/background.png', ],
}
