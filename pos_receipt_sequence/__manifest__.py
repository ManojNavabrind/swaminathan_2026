{
    'name': 'POS Receipt Sequence',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Adds a custom sequence field to POS orders and displays it on receipts',
    'description': 'This module extends pos.order to include a receipt_sequence field with format POS/0001, and ensures it appears on the POS receipt PDF when printing.',
    'author': 'Your Name',
    'depends': ['point_of_sale'],
    'data': [
        'data/pos_sequence_data.xml',
        # 'views/pos_receipt_templates.xml',
        'views/pos_order_tree.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # 'pos_receipt_sequence/static/src/xml/pos_receipt_templates.xml',
            'pos_receipt_sequence/static/src/js/my.js',
            'pos_receipt_sequence/static/src/js/my2.js',

        ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
