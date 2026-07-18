from odoo import api, models, fields, _


class BetopiaGateway(models.Model):
    _name = 'betopia.sms.gateway'
    _description = 'betopia_sms_gateway'

    name = fields.Char(string='Name',required=True)
    gateway = fields.Selection([
        ('alpha_sms','Alpha SMS Gateway'),
        ('greenweb_sms','GreenWeb SMS Gateway'),
        ('adn_sms','ADN SMS Gateway'),

    ],string="Bangladesh Gateway Type",default='alpha_sms',required=True,copy=False)
