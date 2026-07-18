{
    'name': 'Product Catalog',
    'version': '18.0.0.1',
    "summary": """
        This Odoo module extends the product catalog feature to Customer Invoices and Inventory Transfers, offering a user-friendly, POS-style product selection interface to improve speed and accuracy in product entry.
        product catalog Primary keyword,odoo invoice,odoo inventory,odoo inventory management,product catalog management,inventory invoice,product catalog design,product catalogue,wholesale catalogue,odoo inventory module.       
                """,
    'description': """
            This Odoo module extends the product catalog feature to Customer Invoices and Inventory Transfers, offering a user-friendly, POS-style product selection interface to improve speed and accuracy in product entry.
            product catalog Primary keyword,odoo invoice,odoo inventory,odoo inventory management,product catalog management,inventory invoice,product catalog design,product catalogue,wholesale catalogue,odoo inventory module.
    """,
    'author': 'Reliution',
    "website": "https://www.reliution.com",
    "category": "Sales/Sales",

    "license": 'AGPL-3',

    'depends': ['base', 'account', 'stock', 'product'],

    'data': [
        'views/inventory_catalog_view.xml',
    ],

    "images": ['static/description/banner.gif'],
    'price': 60.00,
    'currency': 'USD',
    'application': True,
    'installable': True,

}
