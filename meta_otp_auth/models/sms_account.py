from odoo import api,models,fields


class OtpSmsAccount(models.Model):
    _name = 'otp.sms.account'
    _description ="SMS Account"


    name = fields.Char(string='Name')
    api_key = fields.Char(string='API Key')
    screct_key =fields.Char(string="Screct Key")
