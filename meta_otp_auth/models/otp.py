# -*- coding: utf-8 -*-

from curses import meta
from datetime import datetime, timedelta
from odoo import api,fields, models, _, SUPERUSER_ID
from odoo.http import request
import pyotp
from odoo.exceptions import AccessDenied
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class MetaOtp(models.Model):
    _name= "meta.otp.auth"
    _description = "Otp Records"

    partner_id = fields.Many2one('res.partner', string='Customer', required=True,ondelete='cascade')
    otp = fields.Char(string="Otp")
    expire_time = fields.Integer(string='Expire Time(s)', help='Expire time in Seconds')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False,
        default=lambda self: self.env.company)

    name = fields.Char(compute='_compute_name', string='Name')

    @api.depends('partner_id', 'company_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.company_id.name} verification OTP for {rec.partner_id.name}"


    def get_new_otp(self, partner ):
        otp_time = self.env['ir.default'].sudo()._get('res.config.settings', 'otp_time_limit')
        otp_time = int(otp_time)
        if otp_time < 30:
            otp_time = 30
        #Extra Time added to process OTP
        main_otp_time = otp_time
        totp = pyotp.TOTP(pyotp.random_base32(), interval=main_otp_time, digits=4)
        otp = totp.now()
        _logger.warning('get_new_otp ------ {} >>> {}'.format(type(otp),otp))

        otp_c = self.create({
            'partner_id': partner.id,
            'otp':otp,
            'expire_time':main_otp_time
        })
        self.env.cr.commit()

        return [otp, main_otp_time]

    def is_expired(self):
        self.ensure_one()
        dt_now = datetime.now()
        expire_time = self.create_date + timedelta(seconds = int(self.expire_time))
        if dt_now > expire_time:
            return True
        else:
            return False

    @api.model
    def verify_otp(self, partner_id, otp_value):
        self = self.sudo()

        try:
            otp_int = int(otp_value)
        except (ValueError, TypeError):
            return [False, "Invalid OTP format.", 'error']
        result = [False, "Otp Expired!!! Please send another one.", 'error']
        partner_otp = self.search([
            ('partner_id', '=', partner_id),
            ('otp', '=', otp_int)
        ], order='create_date desc', limit=1)

        if partner_otp:
            if not partner_otp.is_expired():
                partner_otp.partner_id.sudo().otp_varified = True
                result = [True, "Otp Successfully Verified.", 'success']
                partner_otp.sudo().unlink()
            else:
                pass
        else:
            result = [False, "Wrong OTP", 'error']

        return result



    @api.model_create_multi
    def create(self, values_list):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        for values in values_list:
            otps = self.search([['partner_id', '=',values.get('partner_id')]])
            if otps:
                otps.unlink()

        result = super(MetaOtp, self).create(values_list)

        return result

    _sql_constraints = [

        ('unique_customer', 'unique(partner_id)', 'Already Sent an OTP to this Person.')

    ]
