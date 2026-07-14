from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    zencore_dashboard_show_customizer_icon = fields.Boolean(
        string="Show Dashboard Customizer Icon",
        default=True,
    )
    zencore_dashboard_icon_size = fields.Integer(default=70)
    zencore_dashboard_text_size = fields.Integer(default=100)
    zencore_dashboard_corner_radius = fields.Integer(default=96)
    zencore_dashboard_fit_width = fields.Boolean(default=False)
    zencore_dashboard_glassmorphism = fields.Boolean(default=False)
    zencore_dashboard_animations = fields.Boolean(default=True)
    zencore_dashboard_show_greeting_clock = fields.Boolean(default=True)
    zencore_dashboard_show_search = fields.Boolean(default=True)
    zencore_dashboard_background_opacity = fields.Integer(default=34)
    zencore_dashboard_background_image = fields.Binary(attachment=True)

    @api.model
    def _zencore_image_data_url(self, image_data):
        if not image_data:
            return ""
        if isinstance(image_data, bytes):
            image_data = image_data.decode()
        mime_type = "image/png"
        if image_data.startswith("/9j/"):
            mime_type = "image/jpeg"
        elif image_data.startswith("R0lGOD"):
            mime_type = "image/gif"
        elif image_data.startswith("UklGR"):
            mime_type = "image/webp"
        elif image_data.startswith("PHN2Zy"):
            mime_type = "image/svg+xml"
        return "data:%s;base64,%s" % (mime_type, image_data)

    @api.model
    def _zencore_user_param_key(self, name):
        return "zencore_apps_dashboard.%s.%s" % (self.env.user.id, name)

    @api.model
    def _zencore_get_user_int_param(self, name, default):
        value = self.env["ir.config_parameter"].sudo().get_param(
            self._zencore_user_param_key(name),
            default,
        )
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @api.model
    def _zencore_set_user_param(self, name, value):
        self.env["ir.config_parameter"].sudo().set_param(
            self._zencore_user_param_key(name),
            value,
        )

    @api.model
    def zencore_get_dashboard_settings(self):
        user = self.env.user
        def int_setting(field_name, default):
            value = user[field_name]
            return default if value is False or value is None else value

        image_cache_key = user.write_date.strftime("%Y%m%d%H%M%S") if user.write_date else "0"
        background_image = user.sudo().with_context(bin_size=False).zencore_dashboard_background_image
        return {
            "user_id": user.id,
            "user_name": user.name,
            "timezone": user.tz or self.env.context.get("tz") or "UTC",
            "show_customizer_icon": user.zencore_dashboard_show_customizer_icon,
            "icon_size": int_setting("zencore_dashboard_icon_size", 70),
            "text_size": int_setting("zencore_dashboard_text_size", 100),
            "corner_radius": int_setting("zencore_dashboard_corner_radius", 96),
            "app_gap": self._zencore_get_user_int_param("app_gap", 16),
            "fit_width": user.zencore_dashboard_fit_width,
            "glassmorphism": user.zencore_dashboard_glassmorphism,
            "animations": user.zencore_dashboard_animations,
            "show_greeting_clock": user.zencore_dashboard_show_greeting_clock,
            "show_search": user.zencore_dashboard_show_search,
            "background_opacity": int_setting("zencore_dashboard_background_opacity", 34),
            "background_image": bool(background_image),
            "background_image_data_url": self._zencore_image_data_url(background_image),
            "background_image_url": (
                "/web/image/res.users/%s/zencore_dashboard_background_image?unique=%s"
                % (user.id, image_cache_key)
            ),
            "icon_overrides": self.zencore_get_dashboard_icon_overrides(),
        }

    @api.model
    def zencore_save_dashboard_settings(self, values):
        allowed_keys = {
            "show_customizer_icon": "zencore_dashboard_show_customizer_icon",
            "icon_size": "zencore_dashboard_icon_size",
            "text_size": "zencore_dashboard_text_size",
            "corner_radius": "zencore_dashboard_corner_radius",
            "fit_width": "zencore_dashboard_fit_width",
            "glassmorphism": "zencore_dashboard_glassmorphism",
            "animations": "zencore_dashboard_animations",
            "show_greeting_clock": "zencore_dashboard_show_greeting_clock",
            "show_search": "zencore_dashboard_show_search",
            "background_opacity": "zencore_dashboard_background_opacity",
            "background_image": "zencore_dashboard_background_image",
        }
        sanitized = {}
        for key, field_name in allowed_keys.items():
            if key in values:
                sanitized[field_name] = values[key]
        if sanitized.get("zencore_dashboard_background_image") == "":
            sanitized["zencore_dashboard_background_image"] = False
        self.env.user.sudo().write(sanitized)
        if "app_gap" in values:
            self._zencore_set_user_param("app_gap", values["app_gap"])
        return self.zencore_get_dashboard_settings()

    @api.model
    def zencore_get_dashboard_icon_overrides(self):
        icons = self.env["zencore.dashboard.icon"].sudo().with_context(bin_size=False).search([
            ("user_id", "=", self.env.user.id),
        ])
        return [
            {
                "app_key": icon.app_key,
                "app_name": icon.app_name,
                "icon_data_url": self._zencore_image_data_url(icon.icon),
                "icon_url": "/web/image/zencore.dashboard.icon/%s/icon?unique=%s"
                % (icon.id, icon.write_date.strftime("%Y%m%d%H%M%S") if icon.write_date else "0"),
            }
            for icon in icons
        ]

    @api.model
    def zencore_save_dashboard_icon_override(self, values):
        app_key = (values.get("app_key") or "").strip()
        app_name = (values.get("app_name") or "").strip()
        icon_data = values.get("icon")
        if not app_key or not app_name or not icon_data:
            return self.zencore_get_dashboard_icon_overrides()

        Icon = self.env["zencore.dashboard.icon"].sudo()
        icon = Icon.search([
            ("user_id", "=", self.env.user.id),
            ("app_key", "=", app_key),
        ], limit=1)
        vals = {
            "user_id": self.env.user.id,
            "app_key": app_key,
            "app_name": app_name,
            "icon": icon_data,
        }
        if icon:
            icon.write(vals)
        else:
            Icon.create(vals)
        return self.zencore_get_dashboard_icon_overrides()

    @api.model
    def zencore_reset_dashboard_icon_override(self, app_key):
        app_key = (app_key or "").strip()
        if app_key:
            self.env["zencore.dashboard.icon"].sudo().search([
                ("user_id", "=", self.env.user.id),
                ("app_key", "=", app_key),
            ]).unlink()
        return self.zencore_get_dashboard_icon_overrides()
