{
    'name': "POS Rounding",
    'summary': """POS Rounding""",
    'description': """POS Rounding""",

    'category': 'Sales/Point of Sale',
    'author': 'Adevx',
    'license': "OPL-1",
    'website': 'https://adevx.com',
    "price": 0,
    "currency": 'USD',

    'depends': ['point_of_sale', 'account'],
    'data': [
        # views
        'views/account_journal.xml',
        'views/pos_config.xml',
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "adevx_pos_rounding/static/src/**/*"
        ]
    },

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
