# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Swaminathan Reprint Receipt',
    'version': '17.0',
    'category': 'Point Of Sale',
    'sequence': 5,
    'summary': 'Receipt Reprint',
    'description': "Receipt Reprint",
    'website': ' ',
    'author': 'Navabrind IT Solutions',
    # 'version': '11.0.1.0.4',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/receipt_reprint.xml',
        'report/receipt_reprint.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'currency': 'INR',
    'license': 'LGPL-3',

}
