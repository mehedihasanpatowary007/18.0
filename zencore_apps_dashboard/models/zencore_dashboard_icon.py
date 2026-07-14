from odoo import fields, models


class ZencoreDashboardIcon(models.Model):
    _name = "zencore.dashboard.icon"
    _description = "Zencore Dashboard App Icon"
    _rec_name = "app_name"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        ondelete="cascade",
        index=True,
        default=lambda self: self.env.user,
    )
    app_key = fields.Char(required=True, index=True)
    app_name = fields.Char(required=True)
    icon = fields.Binary(attachment=True, required=True)

    _sql_constraints = [
        (
            "zencore_dashboard_icon_user_app_unique",
            "unique(user_id, app_key)",
            "Each user can only define one custom icon for an app.",
        ),
    ]
