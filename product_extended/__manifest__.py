{
    'name': 'Product Extended',
    'description': 'Product form unit price calculation',
    'summary': 'Product form unit price calculation',
    'category': 'Inventory',
    'version': '17.0',
    'author': 'Navabrind IT Solutions',
    'company': 'Navabrind IT Solutions',
    'maintainer': 'Navabrind IT Solutions',
    'website': "",
    'depends': ['sale', 'stock', 'purchase', 'web', 'account'],

    "assets":
        {
            'web.assets_backend': ['product_extended/static/src/js/tax_total_roundoff.js'],
        },

    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/product_category_views.xml',
        'views/sales.xml',
        'data/cron.xml',
        'views/price_evaluation_views.xml',
        'report/report_purchaeorder.xml',
        'report/report_purchasequotation.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
