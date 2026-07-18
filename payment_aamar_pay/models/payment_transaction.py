# -*- coding: utf-8 -*-
import logging

from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_aamar_pay.aamar_pay.payment import AmarPaySession

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator="-", **kwargs):
        """Override to ensure that AamarPay's requirements for references are satisfied."""
        if provider_code == "aamar_pay":
            prefix = payment_utils.singularize_reference_prefix()
        return super()._compute_reference(
            provider_code, prefix=prefix, separator=separator, **kwargs
        )

    def _get_specific_rendering_values(self, processing_values):
        """Return AamarPay-specific rendering values for checkout."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "aamar_pay":
            return res

        provider = self.provider_id

        # Get callback URLs
        try:
            urls = provider._get_urls()
        except Exception:
            urls = {
                "success_url": "/payment/success",
                "fail_url": "/payment/fail",
                "cancel_url": "/payment/cancel",
                "ipn_url": "/payment/ipn",
            }

        rendering_values = {
            "store_id": getattr(provider, "aamarpay_store_id", ""),
            "signature_key": getattr(provider, "aamarpay_signature_key", ""),
            "tran_id": self.reference,
            "amount": self.amount,
            "currency": self.currency_id.name,
            "desc": f"Payment for Order {self.reference}",
            "cus_name": self.partner_id.name or "",
            "cus_email": self.partner_id.email or "",
            "cus_phone": self.partner_id.phone or "",
            "success_url": urls.get("success_url", "/payment/success"),
            "fail_url": urls.get("fail_url", "/payment/fail"),
            "cancel_url": urls.get("cancel_url", "/payment/cancel"),
            "type": "json",
            "cus_add1": self.partner_id.street or "",
            "cus_add2": self.partner_id.street2 or "",
            "cus_city": self.partner_id.city or "",
            "cus_state": (
                self.partner_id.state_id.name if self.partner_id.state_id else ""
            ),
            "cus_postcode": self.partner_id.zip or "",
            "cus_country": (
                self.partner_id.country_id.code if self.partner_id.country_id else "BD"
            ),
        }

        # Determine sandbox/production
        aamarpay_is_sandbox = getattr(provider, "aamarpay_is_sandbox", None)
        if aamarpay_is_sandbox is None:
            aamarpay_is_sandbox = getattr(provider, "state", "") == "test"

        # Initialize AamarPay session
        try:
            mypayment = AmarPaySession(
                aamarpay_is_sandbox=bool(aamarpay_is_sandbox),
                aamarpay_store_id=rendering_values["store_id"],
                aamarpay_signature_key=rendering_values["signature_key"],
            )
        except Exception as exc:
            _logger.exception("Failed to initialize AmarPaySession: %s", exc)
            raise ValidationError(_("AamarPay configuration error: %s") % exc)

        # Set callback URLs
        mypayment.set_urls(
            success_url=rendering_values["success_url"],
            fail_url=rendering_values["fail_url"],
            cancel_url=rendering_values["cancel_url"],
            ipn_url=urls.get("ipn_url"),
        )

        # Product and customer info
        mypayment.set_product_integration(
            tran_id=self.reference,
            amount=str(self.amount),
            desc=f"Payment for {self.reference}",
            product_category="E-commerce",
            product_name=self.payment_method_id.name if self.payment_method_id else "Payment",
            currency=self.currency_id.name,
            num_of_item=1,
            shipping_method="NO",
        )
        mypayment.set_customer_info(
            name=self.partner_id.name or "",
            email=self.partner_id.email or "",
            mobile=self.partner_id.phone or "",
            address1=self.partner_id.street or "",
            address2=self.partner_id.street2 or "",
            city=self.partner_id.city or "",
            state=self.partner_id.state_id.name if self.partner_id.state_id else "",
            postcode=self.partner_id.zip or "",
            country=self.partner_id.country_id.name if self.partner_id.country_id else "Bangladesh",
        )

        # Initialize payment request
        try:
            response = mypayment.init_payment()
        except Exception as exc:
            _logger.exception("Error initializing payment with AamarPay: %s", exc)
            raise ValidationError(_("Payment initialization failed: %s") % exc)

        status = (response.get("status") or "").upper()
        if status == "SUCCESS":
            api_url = (
                response.get("payment_url")
                or response.get("redirect_url")
                or response.get("api_url")
            )
            if api_url:
                rendering_values.update({"api_url": api_url})
                return rendering_values
            else:
                raise ValidationError(_("Payment initialization succeeded but no payment URL returned"))
        else:
            error_msg = response.get("error") or response.get("message") or str(response)
            raise ValidationError(_("Payment initialization failed: %s") % error_msg)

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Find the transaction based on AamarPay data."""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "aamar_pay":
            return tx

        reference = notification_data.get("mer_txnid") or notification_data.get("tran_id")
        if not reference:
            raise ValidationError(_("Missing transaction reference in AamarPay response."))

        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", provider_code)]
        )
        if not tx:
            raise ValidationError(_("No transaction found matching reference %s.") % reference)
        return tx


    def _process_notification_data(self, notification_data):
      super()._process_notification_data(notification_data)

      if self.provider_code != "aamar_pay":
          return

      _logger.info("Processing AamarPay notification data: %s", notification_data)

      self.sudo().provider_reference = (
          notification_data.get("mer_txnid")
          or notification_data.get("tran_id")
      )

      pay_status = (notification_data.get("pay_status") or "").lower()

      # -------------------------------
      # SUCCESS
      # -------------------------------
      if pay_status in ("success", "successful", "completed"):
          self.sudo()._set_done()

          orders = self.sudo().sale_order_ids

          # Fallback linking
          if not orders:
              order = self.env["sale.order"].sudo().search(
                  [("name", "=", self.reference)], limit=1
              )
              if order:
                  self.sudo().write({
                      "sale_order_ids": [(4, order.id)]
                  })
                  orders = order
                  _logger.info(
                      "🔗 Linked transaction %s to Sale Order %s",
                      self.reference, order.name
                  )

          # Confirm orders ONLY (no _set_paid in Odoo 18)
          for order in orders:
              if order.state not in ("sale", "done"):
                  order.sudo().action_confirm()
                  _logger.info("✅ Sale Order %s confirmed", order.name)

      # -------------------------------
      # FAILURE / CANCEL
      # -------------------------------
      elif pay_status in ("failed", "cancelled", "canceled"):
          self.sudo()._set_canceled()

      # -------------------------------
      # UNKNOWN
      # -------------------------------
      else:
          err = (
              notification_data.get("error")
              or notification_data.get("message")
              or "Unknown payment error"
          )
          self.sudo()._set_error(err)




    # def _process_notification_data(self, notification_data):
    #   """Process notification/IPN data for AamarPay (Odoo 18 compatible)."""
    #   super()._process_notification_data(notification_data)

    #   if self.provider_code != "aamar_pay":
    #       return

    #   _logger.info("Processing AamarPay notification data: %s", notification_data)

    #   self.provider_reference = (
    #       notification_data.get("mer_txnid")
    #       or notification_data.get("tran_id")
    #   )

    #   pay_status = (notification_data.get("pay_status") or "").lower()

    #   # -------------------------------
    #   # SUCCESS
    #   # -------------------------------
    #   if pay_status in ("success", "successful", "completed"):
    #       self._set_done()

    #       # Get linked sale orders (M2M in Odoo 18)
    #       orders = self.sale_order_ids

    #       # Fallback: link order by reference
    #       if not orders:
    #           order = self.env["sale.order"].sudo().search(
    #               [("name", "=", self.reference)], limit=1
    #           )
    #           if order:
    #               self.sudo().write({
    #                   "sale_order_ids": [(4, order.id)]
    #               })
    #               orders = order
    #               _logger.info(
    #                   "🔗 Linked transaction %s to Sale Order %s",
    #                   self.reference, order.name
    #               )

    #       # Confirm & mark orders as paid
    #       for order in orders:
    #           if order.state not in ("sale", "done"):
    #               order.sudo().action_confirm()

    #           order.sudo()._set_paid()
    #           _logger.info(
    #               "💰 Sale Order %s confirmed and marked as paid",
    #               order.name
    #           )

    #   # -------------------------------
    #   # FAILURE / CANCEL
    #   # -------------------------------
    #   elif pay_status in ("failed", "cancelled", "canceled"):
    #       self._set_canceled()

    #   # -------------------------------
    #   # UNKNOWN STATE
    #   # -------------------------------
    #   else:
    #       err = (
    #           notification_data.get("error")
    #           or notification_data.get("message")
    #           or "Unknown payment error"
    #       )
    #       self._set_error(err)


    # def _process_notification_data(self, notification_data):
    #     """Process notification/IPN data for AamarPay."""
    #     super()._process_notification_data(notification_data)
    #     if self.provider_code != "aamar_pay":
    #         return

    #     _logger.info("Processing AamarPay notification data: %s", notification_data)

    #     self.provider_reference = notification_data.get("mer_txnid") or notification_data.get("tran_id")
    #     pay_status = (notification_data.get("pay_status") or "").lower()

    #     if pay_status in ("success", "successful", "completed"):
    #         self._set_done()

    #         # -------------------------------
    #         # Automatic sale order linking & payment
    #         # -------------------------------
    #         order = self.sale_order_id
    #         if not order:
    #             order = self.env["sale.order"].sudo().search([("name", "=", self.reference)], limit=1)
    #             if order:
    #                 self.sudo().sale_order_id = order.id
    #                 _logger.info("🔗 Linked transaction %s to Sale Order %s", self.reference, order.name)

    #         if order:
    #             # Confirm quotation if not confirmed
    #             if order.state not in ("sale", "done"):
    #                 order.sudo().action_confirm()
    #             # Mark order as paid
    #             order.sudo()._set_paid()
    #             _logger.info("💰 Sale Order %s confirmed and marked as paid", order.name)

    #     elif pay_status in ("failed", "cancelled", "canceled"):
    #         self._set_canceled()
    #     else:
    #         err = notification_data.get("error") or notification_data.get("message") or "Unknown payment error"
    #         self._set_error(err)
