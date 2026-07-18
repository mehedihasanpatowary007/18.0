# -*- coding: utf-8 -*-

import re
from datetime import datetime
from odoo.tools import email_normalize
from odoo import api,fields, models, _
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.fields import Datetime as odoo_datetime
import requests
import logging

_logger = logging.getLogger(__name__)

EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\+?\d{1,3}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'

def is_email(string):
        try:
            email_normalize(string)
            return True
        except ValueError:
            return False

def is_phone_number(string):

    phone = re.sub(r'\D', '', string)
    if re.match(r'^\+?8801[3-9]\d{8}$', phone):
        phone = phone[-10:]
    elif re.match(r'^\+?880-1[3-9]\d{3}-\d{5}$', phone):

        phone = phone[-11:-8] + phone[-7:-4] + phone[-3:]
    elif re.match(r'^01[3-9]\d{2}-\d{3}-\d{4}$', phone):

        phone = phone[:3] + phone[4:7] + phone[8:]
    elif re.match(PHONE_PATTERN, phone):
        pass
    else:
        return False

    print(f'is_phone_number {phone}')
    return phone

def normalize_mobile(mobile):

    if not mobile:
        return False
    mobile = re.sub(r'\D', '', str(mobile))
    if mobile.startswith('880'):
        mobile = mobile[2:]
    elif mobile.startswith('0'):
        mobile = mobile[1:]
    return mobile


class MetaResPartner(models.Model):

    _inherit = 'res.partner'

    otp_varified = fields.Boolean(
        string='Otp varified', default=False
        )

    def send_otp(self):

        send_otp_model = self.env['send.otp']
        otp_model = self.env["meta.otp.auth"]
        Mail = self.env['mail.mail']

        for partner in self:

            contact = partner.email or partner.mobile or partner.phone

            otp_record = otp_model.search([('partner_id', '=', partner.id)], order='create_date desc', limit=1)

            if not otp_record or otp_record.is_expired():
                otp_record = otp_model.get_new_otp(partner)
                if contact:
                    if partner.email:
                        MailServer = self.env['ir.mail_server'].sudo().search([], limit=1)
                        email_from = MailServer.smtp_user or MailServer.email

                        mail_values = {
                            'subject': 'Your OTP Code',
                            'body_html': f'<p>Hi {partner.name or "User"},</p>'
                                        f'<p>Your OTP code is <b>{otp_record[0]}</b>.</p>',
                            'email_to': partner.email,
                            'email_from': email_from,  # ✅ dynamically from mail server
                        }

                        print("########OTP",mail_values)
                        mail = Mail.sudo().create(mail_values)
                        mail.sudo().send()

                        resp = [True, f'OTP sent to email {partner.email}. Valid for {otp_record[1]} seconds.', 'success']
                    else:

                        send_otp_model.email_send_otp(partner.name or 'User', otp_record[0], contact)
                        resp = [True, f'OTP sent to mobile {contact}. Valid for {otp_record[1]} seconds.', 'success']
                else:
                    resp = [False, 'Unable to send OTP. No email or mobile number found.', 'error']
            else:

                remaining = int(otp_record.expire_time - (datetime.now() - otp_record.create_date).total_seconds())
                resp = [True, f'Already sent an OTP. Please try after {remaining} seconds.', 'warning']

            return resp

    def send_sms_otp(self):
        otp_model = self.env["meta.otp.auth"]

        for partner in self:
            otp_record = otp_model.search(
                [('partner_id', '=', partner.id)],
                order='create_date desc',
                limit=1
            )

            if not otp_record or otp_record.is_expired():
                otp_record = otp_model.get_new_otp(partner)  # must return (otp_code, expire_minutes)

                message = f"Your OTP code is {otp_record[0]}. It is valid for {otp_record[1]} seconds."
                _logger.info("Generated OTP for %s: %s", partner.id, message)

                if partner.mobile:
                    mobile = str(partner.mobile).strip()
                    if not mobile.startswith("88"):
                        mobile = "88" + mobile
                else:
                    _logger.error("Partner %s has no mobile number", partner.id)
                    return [False, "No mobile number found", 'error']


                headers = {"Accept": "application/json"}

                api_end_point = (
                    self.env["ir.default"]
                    .sudo()
                    ._get("res.config.settings", "api_end_point")
                )
                api_key = (
                    self.env["ir.default"]
                    .sudo()
                    ._get("res.config.settings", "api_key")
                )
                api_secret_key = (
                    self.env["ir.default"]
                    .sudo()
                    ._get("res.config.settings", "api_secret_key")
                )

                payload = {
                      "api_key": api_key,
                      "api_secret": api_secret_key,
                      "request_type": "SINGLE_SMS",
                      "message_type":"TEXT",
                      "mobile": mobile,
                      "message_body": message,

                  }
                try:
                    resp = requests.post(api_end_point, json=payload, headers=headers, timeout=15)
                    data = resp.json()
                    _logger.info("OTP Sent to %s | Response: %s", partner.mobile, data)
                    print(data)

                    if data.get('api_response_message') == 'SUCCESS':
                        return [True, f'OTP sent to mobile {mobile}.', 'success']
                    else:
                        return [False, data.get('msg', 'Failed to send OTP'), 'error']
                except Exception as e:
                    _logger.error("Failed to send OTP to %s: %s", partner.mobile, e)
                    return [False, str(e), 'error']
            else:
                remaining = int(otp_record.expire_time - (odoo_datetime.now() - otp_record.create_date).total_seconds())
                return [True, f'Already sent an OTP. Please try after {remaining} seconds.', 'warning']


class Users(models.Model):

    _inherit = 'res.users'

    @api.model
    def _check_credentials(self, password, env):
        if request.params.get('auth_type', 'password') == 'password':
            return super()._check_credentials(password, env)

        verify_otp= self.env["meta.otp.auth"].sudo().verify_otp(self.partner_id.id, password)
        if not verify_otp[0]:
            raise AccessDenied()

    @api.model_create_multi

    def create(self, val_list):

        for vals in val_list:
            _logger.warning("User create Values *************** {}".format(vals))
            if isinstance(vals['login'], (tuple, list)):
                vals['login'] = vals['login'][0]
            else: vals['login'] = vals['login']
            valid_phone = is_phone_number(vals['login'])
            if valid_phone:
                vals['phone'] = valid_phone
                vals['mobile'] = valid_phone
                vals.pop('email',False)
        return super(Users, self).create(val_list)

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        create_mode = bool(self.env.context.get('create_user'))
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)
        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            mobile = user.email
            sms_text = self.env['ir.default'].sudo()._get('res.config.settings', 'reset_pass_content').replace('<name>', user.name)
            self.env['send.sms'].send_sms(mobile, sms_text)
            _logger.warning("Sending Non Cash Payment SMS-------->")

