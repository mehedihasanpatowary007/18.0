
from odoo import fields, models,api, _
import requests
from odoo.exceptions import ValidationError
import re

class SmsBuilder(models.TransientModel):
    _name = 'sms.builder'
    _description = 'SMS Builder'

    partner_id = fields.Many2one('res.partner', string='Recipient')
    receiving_number = fields.Char(
        string='Receiving Number',
        compute='_compute_receiving_number',
        required=True
    )
    template_id = fields.Many2one('betopia.sms.template', string='Select Template')
    text_message = fields.Text(string='Message', required=True)
    sms_account = fields.Many2one('betopia.sms.account', string='SMS Account')

    @api.depends('partner_id.mobile', 'partner_id.phone')
    def _compute_receiving_number(self):
        for rec in self:
            rec.receiving_number = rec.partner_id.mobile or rec.partner_id.phone

    @api.onchange('template_id')
    def _onchange_template_id(self):
        for rec in self:
            if rec.template_id:
                rec.text_message = f"{(rec.template_id.body or '') + (rec.template_id.footer_text or '')}"

    @staticmethod
    def _clean_number(number):
        if not number:
            return ''
        return re.sub(r'\D', '', number)
    def action_confirm_sms(self):
        self.ensure_one()

        # Account selection priority
        if self.sms_account:
            account = self.sms_account
        elif self.template_id and self.template_id.sms_account:
            account = self.template_id.sms_account
            # self.text_message = f"{(self.template_id.body or '') + (self.template_id.footer_text or '')}"
        else:
            raise ValidationError(_("Please select an SMS Account or Template with account."))

        url = account.api_end_point
        api_key = account.api_key
        api_secret_key = account.api_secret_key

        payload = {
            "api_key": api_key,
            "api_secret": api_secret_key,
            "request_type": "SINGLE_SMS",
            "message_type": "TEXT",
            "mobile": self._clean_number(self.receiving_number),
            "message_body": self.text_message,
        }

        print("####PAYLOAD", payload)
        response = requests.post(url, data=payload)
        res_json = response.json()
        print("RES###",res_json)

        if res_json.get('api_response_code') == 200:
            message_data = _("Message Sent!")
            self.env['betopia.sms.message'].sudo().create({
                'partner_id': self.partner_id.id,
                'mobile_number': self.receiving_number,
                'body': self.text_message,
                'sms_account':self.sms_account.id,
                'state': 'sent',
                'response':res_json,
            })
            type_data = "success"
        else:
            message_data = _("Message Not Sent!")
            self.env['betopia.sms.message'].sudo().create({
                'partner_id': self.partner_id.id,
                'mobile_number': self.receiving_number,
                'body': self.text_message,
                'sms_account':self.sms_account.id,
                'state': 'failed',
                'response':res_json,

            })
            type_data = "warning"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message_data,
                'type': type_data,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }



