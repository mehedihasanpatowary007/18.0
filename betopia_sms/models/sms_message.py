from odoo import models, fields, api
import requests
import logging
import re
 
_logger = logging.getLogger(__name__)

class BetopiaSMSMessage(models.Model):
    _name = 'betopia.sms.message'
    _description = 'Betopia SMS Message'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Recipient', help='Receiving User')
    sms_account = fields.Many2one('betopia.sms.account', string='SMS Account', required=True)
    mobile_number = fields.Char(string='Receiving Number', required=True)
    state = fields.Selection([
        ('outgoing', 'In Queue'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered')], string="State", default='outgoing')
    template_id = fields.Many2one('betopia.sms.template', string="Template")
    body = fields.Text(string="Body")
    response = fields.Text(string='Response')


    def send_sms(self):
        results = []
        for record in self:
            try:
                # determine account (template override > record account)
                sms_account = None
                if record.template_id and getattr(record.template_id, 'sms_account', False):
                    sms_account = record.template_id.sms_account
                elif record.sms_account:
                    sms_account = record.sms_account

                if not sms_account:
                    _logger.error("No SMS account configured for Betopia message (id=%s).", record.id)
                    record.state = 'failed'
                    results.append(False)
                    continue

                url = getattr(sms_account, 'api_end_point', None)
                api_key = getattr(sms_account, 'api_key', None)
                api_secret_key = getattr(sms_account, 'api_secret_key', None)

                # choose message body
                if record.body:
                    msg = record.body
                elif record.template_id:
                    msg = f"{record.template_id.body or ''} {record.template_id.footer_text or ''}"
                else:
                    msg = "Test message"

                # clean mobile number
                mobile_number = re.sub(r'\D', '', (record.mobile_number or ''))
                if not mobile_number or len(mobile_number) < 7:  # basic sanity check
                    _logger.error("Invalid mobile number for Betopia message id=%s: %s", record.id, record.mobile_number)
                    record.state = 'failed'
                    results.append(False)
                    continue

                # gateway type detection (safe attribute access)
                # gateway_type = 'alpha_sms'
                # if getattr(sms_account, 'gateway_id', False):
                #     gateway_type = getattr(sms_account.gateway_id, 'gateway', 'alpha_sms') or 'alpha_sms'

                payload = {
                      "api_key": api_key,
                      "api_secret": api_secret_key,
                      "request_type": "SINGLE_SMS",
                      "message_type":"TEXT",
                      "mobile": mobile_number,
                      "message_body": msg,

                  }

                _logger.info("Sending SMS (msg len=%s) to %s via %s", len(msg), mobile_number, url)
                try:
                    response = requests.post(url, data=payload, timeout=30)
                except requests.exceptions.RequestException as e:
                    _logger.exception("Request failed while sending SMS to %s: %s", mobile_number, e)
                    record.state = 'failed'
                    results.append(False)
                    continue

                _logger.info("SMS API response [%s]: %s", response.status_code, response.text[:400])

                # interpret response
                success = False
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        _logger.debug("SMS API JSON response: %s", response_data)
                        success = True
                    except ValueError:
                        # not JSON — fallback to text checks
                        success = 'success' in response.text.lower()
                else:
                    _logger.error("SMS API returned HTTP %s for record %s", response.status_code, record.id)
                    success = False

                # set state accordingly
                record.state = 'sent' if success else 'failed'
                results.append(success)

            except Exception as e:
                _logger.exception("Unexpected error in Betopia send_sms for record %s: %s", record.id, e)
                record.state = 'failed'
                results.append(False)

        # Return True only if every message was successful
        return all(results)
