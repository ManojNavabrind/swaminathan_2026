{
    "name": "POS Receipt Customization",
    "version": "23.01",
    "category": "customization",
    "summary": "POS Receipt Customization",
    "author": "Odooistic",
    'website': "http://www.odooistic.co.uk/",
    "depends": ['product','product_extended'],
    "data": [
            'views/res_company_views.xml'
    ],
    'assets'  :  {
                'point_of_sale._assets_pos': [ "pos_order_receipt_customization/static/src/xml/pos_customizations.xml" ,
                                               "pos_order_receipt_customization/static/src/js/pos_discount_patch.js",
                                               "pos_order_receipt_customization/static/src/js/client_name.js",
                                               "pos_order_receipt_customization/static/src/js/models.js",
                                               'pos_order_receipt_customization/static/src/scss/pos.scss',
                                               ],
            },
    "installable": True,
}

