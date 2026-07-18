from odoo import models, fields, _
import logging
import requests

_logger = logging.getLogger(__name__)

class PoSOrderInherit(models.Model):
    _inherit = 'pos.order'

    direct_invoice_link = fields.Char("Direct Invoice Link", readonly=True)

    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()
        for order in self:
            # Skip if order is not in paid state
            if order.state != 'paid':
                continue

            _logger.info(f"Processing POS order {order.name} for invoice and SMS")

            # Ensure invoice exists
            if not order.account_move:
                order.write({'to_invoice': True})
                try:
                    _logger.info(f"Creating invoice for POS order {order.name}")
                    order.action_pos_order_invoice()

                    if order.account_move:
                        _logger.info(f"Invoice created: {order.account_move.name}")
                        # Ensure the invoice is posted
                        if order.account_move.state == 'draft':
                            order.account_move.with_context(skip_invoice_sync=True)._post()
                            _logger.info(f"Invoice posted: {order.account_move.name}")
                except Exception as e:
                    _logger.error('Could not create invoice for POS Order %s: %s', order.name, str(e))
                    continue

            # Build portal link
            if order.account_move and order.account_move.is_sale_document():
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
                access_token = order.account_move._portal_ensure_token()
                access_link = f"/my/invoices/{order.account_move.id}?access_token={access_token}"
                full_link = f"{base_url}{access_link}"

                # Shorten the link
                # short_link = self._shorten_url(full_link)

                order.write({'direct_invoice_link': full_link})
                _logger.info(f"Portal link created for order {order.name}: {full_link}")

                # Send SMS
                self._send_invoice_sms(order, full_link)

        return res

    def _send_invoice_sms(self, order, invoice_link):
        """Send SMS with invoice link to customer"""
        if not order.partner_id:
            _logger.info(f"No partner assigned to order {order.name}, skipping SMS")
            return

        mobile_number = order.partner_id.mobile or order.partner_id.phone
        if not mobile_number:
            _logger.info(f"No mobile/phone number for partner {order.partner_id.name}, skipping SMS")
            return

        # Build SMS text
        sms_text = (
            f"Thank you {order.partner_id.name or 'Customer'} for shopping at {order.company_id.name}.\n"
            f"Purchase amount: {order.currency_id.format(order.amount_total)}\n"
            f"Invoice: {invoice_link}"
        )
        print(sms_text)

        # Send via Betopia SMS
        try:
            sms_account = self.env['betopia.sms.account'].search([], limit=1)
            if sms_account:
                sms_record = self.env['betopia.sms.message'].create({
                    'name': f"POS SMS: {order.pos_reference or order.name}",
                    'partner_id': order.partner_id.id,
                    'sms_account': sms_account.id,
                    'mobile_number': mobile_number,
                    'body': sms_text,
                })
                sms_record.send_sms()
                _logger.info(f"SMS sent for order {order.name} to {mobile_number}")
            else:
                _logger.warning("No Betopia SMS account found, SMS not sent")
        except Exception as e:
            _logger.error('Could not send SMS for POS Order %s: %s', order.name, str(e))

    # def _shorten_url(self, long_url):
    #     """Shorten a URL using TinyURL"""
    #     try:
    #         resp = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}")
    #         if resp.status_code == 200:
    #             return resp.text
    #     except Exception as e:
    #         _logger.warning(f"Failed to shorten URL {long_url}: {e}")
    #     return long_url  # fallback to original




