# -*- coding: utf-8 -*-
{
    'name': "betopia_sms",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account','sale_management', 'purchase','point_of_sale',],


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_views.xml',
        'views/gateway_views.xml',
        'views/message_views.xml',
        'views/templates_views.xml',
        'views/manu_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/sms_builder.xml',
        'views/purchase_order_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'betopia_sms/static/src/js/pos_patch.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

