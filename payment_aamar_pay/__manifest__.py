# -*- coding: utf-8 -*-
{
    'name': "payment_aamar_pay",

    'summary': "A Payment provider covering Bangladesh.",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Payment Providers',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/payment_aamar_pay_templates.xml',
        'views/payment_provider_views.xml',
        
        'data/payment_methods_data.xml',
        'data/payment_provider_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}

