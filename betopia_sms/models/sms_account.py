
from odoo import models, fields, api,_
from odoo.exceptions import UserError
import requests


class BetopiaSMSAccount(models.Model):
    _name = 'betopia.sms.account'
    _description = 'betopia_sms_account'

    name = fields.Char(string='Name',required=True)
    gateway_id = fields.Many2one('betopia.sms.gateway',required=True,copy=False,ondelete='cascade')

    api_end_point = fields.Char(string='API End Point',required =True)
    api_key = fields.Char(string='API Key',required=True)
    api_secret_key = fields.Char(string="API Secret Key",required =True)
