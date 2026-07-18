# -*- coding: utf-8 -*-

{
    "name": "Website OTP Authentication",
    "summary": "Odoo Website OTP Authentication makes secure environment in your Odoo website for your portal users.",
    "category": "Website",
    "version": "18.0.1.0",  # <-- Updated version for Odoo 18
    "sequence": 1,
    "author": "Metamorphosis Ltd",
    "license": "LGPL-3",  # <-- Changed to a valid license for Odoo
    "website": "https://metamorphosis.com.bd/",
    "description": """OTP
One Time Authentication Password
OTP Authentication
Website OTP Authentication
Odoo Website OTP Authentication
One Time Password
One Time Password Authentication
Access Management
SMS OTP
SMS One Time Password
Odoo OTP SMS Notification
Login via OTP
Login via OTP Authentication
Odoo
Website""",
    "version": "18.0.1.0",
    "depends": ["web", "website", "portal", "auth_signup"],
    "external_dependencies": {"python": ["pyotp"], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/auth_signup_login_templates.xml",
        "views/webclient_templates.xml",
        "views/res_config_views.xml",
        "views/res_user_view.xml",
        "views/otp_view.xml",
        "data/data_otp.xml",
    ],

    "images": ["static/description/Banner.png"],
    "application": True,
    "installable": True,
    "auto_install": False,
    "price": 65,
    "currency": "USD",
    "pre_init_hook": "pre_init_check",
}
