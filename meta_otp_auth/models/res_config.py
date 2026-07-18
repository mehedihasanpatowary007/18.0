
from odoo import api, fields, models, _


class WebsiteOTPSettings(models.TransientModel):
    _inherit = "res.config.settings"

    signin_auth = fields.Boolean(string="Sign-in OTP Authentication")
    signup_auth = fields.Boolean(string="Sign-up OTP Authentication")
    otp_time_limit = fields.Integer("OTP Time Limit (sec)", help="OTP expiry time")
    otp_content = fields.Text("OTP SMS Content")
    otp_sms_provider = fields.Selection(
        [("adn", "Adn SMS Gateway")],
        string="OTP SMS Provider",
    )

    # Adn
    api_end_point = fields.Char(string='API End Point')
    api_key = fields.Char(string='API Key')
    api_secret_key = fields.Char(string="API Secret Key")

    # @api.multi
    def set_values(self):
        super(WebsiteOTPSettings, self).set_values()
        IrDefault = self.env["ir.default"].sudo()
        IrDefault.set("res.config.settings", "signin_auth", self.signin_auth)
        IrDefault.set("res.config.settings", "signup_auth", self.signup_auth)
        IrDefault.set("res.config.settings", "otp_time_limit", self.otp_time_limit)
        IrDefault.set("res.config.settings", "otp_content", self.otp_content)
        IrDefault.set("res.config.settings", "otp_sms_provider", self.otp_sms_provider)

        IrDefault.set("res.config.settings", "api_end_point", self.api_end_point)
        IrDefault.set("res.config.settings", "api_key", self.api_key)
        IrDefault.set("res.config.settings", "api_secret_key", self.api_secret_key)
        return True

    # @api.multi
    def get_values(self):
        res = super(WebsiteOTPSettings, self).get_values()
        IrDefault = self.env["ir.default"].sudo()
        res.update(
            {
                "signin_auth": IrDefault._get(
                    "res.config.settings", "signin_auth", self.signin_auth
                ),
                "signup_auth": IrDefault._get(
                    "res.config.settings", "signup_auth", self.signup_auth
                ),
                "otp_content": IrDefault._get(
                    "res.config.settings", "otp_content", self.otp_content
                ),
                "otp_sms_provider": IrDefault._get(
                    "res.config.settings", "otp_sms_provider", self.otp_sms_provider
                ),
                "api_end_point": IrDefault._get(
                    "res.config.settings", "api_end_point", self.api_end_point
                ),
                "api_key": IrDefault._get(
                    "res.config.settings", "api_key", self.api_key
                ),
                "api_secret_key": IrDefault._get(
                    "res.config.settings", "api_secret_key", self.api_secret_key
                ),
            }
        )
        return res
