{
    "name": "Website Product Cart Quantity Limit",
    "version": "18.0.1.0.6",
    "category": "Website/Website",
    "summary": "Limit website cart quantity per product",
    "author": "Mehedi Hasan",
    "website": "https://www.zencoreltd.com",
    "license": "LGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/product_template_views.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_product_cart_limit/static/src/js/cart_limit.js",
            "website_product_cart_limit/static/src/scss/cart_limit.scss",
        ],
    },
    "installable": True,
    "application": False,
}
