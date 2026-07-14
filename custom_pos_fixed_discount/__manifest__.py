{
    "name": "POS Fixed Line Discount",
    "version": "18.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Add fixed amount discounts on POS order lines",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/pos_order_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "custom_pos_fixed_discount/static/src/js/**/*.js",
            "custom_pos_fixed_discount/static/src/xml/**/*.xml",
        ],
    },
    "installable": True,
    "application": False,
}
