import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('aamar_pay', 'aamarPay Payment Gateway')],
        ondelete={'aamar_pay': 'set default'}
    )

    aamarpay_store_id = fields.Char(
        string="aamarPay Store ID",
        required_if_provider='aamar_pay',
        help="Your Store ID from the AamarPay merchant panel"
    )
    aamarpay_signature_key = fields.Char(
        string="aamarPay Signature Key",
        required_if_provider='aamar_pay',
        help="Your Signature Key from the AamarPay merchant panel"
    )
    aamarpay_is_sandbox = fields.Boolean(
        "Sandbox Mode",
        default=True,
        help="Enable sandbox mode to use test credentials with AamarPay"
    )

    # def _get_urls(self):
    #     base_url = self.get_base_url()
    #     return {
    #         "success_url": f"{base_url}payment/success",
    #         "fail_url": f"{base_url}payment/fail",
    #         "cancel_url": f"{base_url}payment/cancel",
    #         "ipn_url": f"{base_url}payment/ipn",
    #     }

    def _get_urls(self):
        base_url = self.get_base_url().rstrip('/')
        
        # Force HTTPS for payment callbacks
        if base_url.startswith('http://'):
            base_url = base_url.replace('http://', 'https://', 1)
        
        urls = {
            "success_url": f"{base_url}/payment/success",
            "fail_url": f"{base_url}/payment/fail",
            "cancel_url": f"{base_url}/payment/cancel",
            "ipn_url": f"{base_url}/payment/ipn",
        }
        
        _logger.info("AamarPay callback URLs: %s", urls)
        return urls


    def _get_default_payment_method_codes(self):
        if self.code == 'aamar_pay':
            return ['aamar_pay']
        return super()._get_default_payment_method_codes()
