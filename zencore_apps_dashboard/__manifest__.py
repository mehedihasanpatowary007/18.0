{
    "name": "Zencore Apps Dashboard",
    "summary": "Customizable apps dashboard for Odoo 18",
    "version": "18.0.1.0.0",
    "category": "Extra Tools",
    "author": "Zencore",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "security/zencore_dashboard_icon_rules.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "zencore_apps_dashboard/static/src/js/zencore_apps_dashboard.js",
            "zencore_apps_dashboard/static/src/scss/zencore_apps_dashboard.scss",
        ],
    },
    "installable": True,
    "application": True,
}
