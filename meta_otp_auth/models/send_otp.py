# -*- coding: utf-8 -*-
import logging
import requests
import base64
import json
import string
import random
from odoo import api, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import requests
import logging
import re

_logger = logging.getLogger(__name__)

class SendOtp(models.TransientModel):

    _name = "send.otp"

    def email_send_otp(self, userName, otp, mobile):
        userObj = (
            self.env["res.users"]
            .sudo()
            .search(["|", ("login", "=", mobile), ("mobile", "=", mobile)], limit=1)
        )

        if not userName and userObj:
            userName = userObj.name

        if userObj and userObj.partner_id and userObj.partner_id.email_normalized:
            try:
                otp_obj = (
                    self.env["meta.otp.auth"]
                    .sudo()
                    .search([("partner_id", "=", userObj.partner_id.id)], limit=1)
                )

                template = self.env.ref("meta_otp_auth.email_template_user_otp").sudo()
                logging.info(
                    f"to send otp {otp} ------ Sending OTP {otp_obj.otp} email -----------  via template{template}"
                )
                template.send_mail(
                    otp_obj.id,
                    force_send=True,
                    email_layout_xmlid="mail.mail_notification_light",
                )
            except Exception as e:
                logging.exception(f"Error While sending OTP Email {e}")
                pass

        if mobile:
            logging.info(
                    f"to send otp {otp} ------ to mobile ----------- {mobile}"
                )
            sms_provider = (
                self.env["ir.default"]
                .sudo()
                ._get("res.config.settings", "otp_sms_provider")
            )
            sms_text = (
                self.env["ir.default"]
                .sudo()
                ._get("res.config.settings", "otp_content")
                .replace("<otp>", f"{str(otp)}")
            )
            logging.info(f"sms_text:------------------------ {sms_text}")

            if sms_provider == "adn":

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
                      "message_body": sms_text,

                  }



                _logger.info("Sending SMS (msg len=%s) to %s via %s", len(sms_text), mobile, api_end_point)
                try:
                    response = requests.post(api_end_point, data=payload, timeout=30)
                except requests.exceptions.RequestException as e:
                    _logger.exception("Request failed while sending SMS to %s: %s", mobile, e)

                _logger.info("SMS API response [%s]: %s", response.status_code, response.text[:400])


            return {
                'status': 'error',
                'message': 'Invalid SMS provider configuration',
                'response': None
            }

        return True
