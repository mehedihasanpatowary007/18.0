# -*- coding: utf-8 -*-
import logging
import hashlib
import json

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AamarPayController(http.Controller):
    """Controller handling AamarPay return URLs and IPN callbacks."""

    _success_url = "/payment/success"
    _fail_url = "/payment/fail"
    _cancel_url = "/payment/cancel"
    _ipn_url = "/payment/ipn"

    # -------------------------------
    # SUCCESS ROUTE
    # -------------------------------
    @http.route("/payment/success", type="http", auth="public", csrf=False, website=True)
    def aamarpay_success(self, **data):
      _logger.info("✅ AamarPay Success Data: %s", data)

      # 🔁 If user refreshes page (no gateway data)
      if not data:
          _logger.warning("⚠️ Empty success callback — redirecting to confirmation")
          return request.redirect("/shop/confirmation")

      try:
          tx = request.env["payment.transaction"].sudo()._get_tx_from_notification_data(
              "aamar_pay", data
          )

          _logger.info("🔎 TX Reference: %s", tx.reference)

          # Process notification (idempotent)
          if tx.state != "done":
              tx._process_notification_data(data)
              _logger.info("✅ Payment marked as DONE for tx: %s", tx.reference)

          # Ensure sale order is available for confirmation page
          orders = tx.sale_order_ids
          if orders:
              request.session["sale_last_order_id"] = orders[0].id
              _logger.info("🧾 sale_last_order_id set to %s", orders[0].name)

      except Exception as e:
          _logger.exception("❌ Error handling AamarPay success: %s", e)

      # 🚀 ALWAYS redirect (never render here)
      return request.redirect("/shop/confirmation")

    # -------------------------------
    # FAIL ROUTE
    # -------------------------------
    @http.route(_fail_url, type="http", auth="public", csrf=False)
    def aamarpay_fail(self, **data):
        """Handle failed payment from AamarPay."""
        _logger.info("⚠️ AamarPay Fail Data: %s", data)
        try:
            tx = request.env["payment.transaction"].sudo()._get_tx_from_notification_data("aamar_pay", data)
            tx._set_error("Payment failed on AamarPay.")
            return request.redirect("/shop/confirmation")
        except Exception as e:
            _logger.exception("❌ Error handling AamarPay failure: %s", e)
            return request.redirect("/shop/confirmation")

    # -------------------------------
    # CANCEL ROUTE
    # -------------------------------
    @http.route(_cancel_url, type="http", auth="public", csrf=False)
    def aamarpay_cancel(self, **data):
        """Handle payment cancellation from AamarPay."""
        _logger.info("⚠️ AamarPay Cancel Data: %s", data)
        try:
            tx = request.env["payment.transaction"].sudo()._get_tx_from_notification_data("aamar_pay", data)
            tx._set_canceled()
            return request.redirect("/shop/confirmation")
        except Exception as e:
            _logger.exception("❌ Error handling AamarPay cancellation: %s", e)
            return request.redirect("/shop/confirmation")

    # -------------------------------
    # IPN CALLBACK
    # -------------------------------
    @http.route(_ipn_url, type="http", auth="public", methods=["POST"], csrf=False)
    def aamarpay_ipn(self, **post):
        """Handle IPN (Instant Payment Notification) from AamarPay."""
        raw_data = request.httprequest.data.decode("utf-8")
        form_data = dict(request.httprequest.form)

        _logger.info("📩 AamarPay raw IPN: %s", raw_data)
        _logger.info("📩 AamarPay form IPN: %s", form_data)

        try:
            data = form_data or (json.loads(raw_data) if raw_data else {})
        except Exception as e:
            _logger.error("❌ Could not parse IPN payload: %s", e)
            return http.Response("Invalid payload", status=400)

        if not data:
            return http.Response("No data received", status=400)

        transaction_id = data.get("tran_id") or data.get("mer_txnid")
        amount = data.get("amount")
        received_hash = data.get("hash")

        if not transaction_id or not amount:
            return http.Response("Missing parameters", status=400)

        # Optional hash check - using your existing secret key parameter
        secret_key = request.env["ir.config_parameter"].sudo().get_param(
            "delivery_steadfast.secret_key"
        )
        if received_hash:
            hash_string = f"{transaction_id}{amount}{secret_key}"
            calculated_hash = hashlib.sha256(hash_string.encode()).hexdigest()
            if received_hash != calculated_hash:
                return http.Response("Invalid hash", status=400)

        # Find transaction
        tx = request.env["payment.transaction"].sudo()._get_tx_from_notification_data("aamar_pay", data)
        if not tx:
            return http.Response("Transaction not found", status=404)

        # Update transaction state
        pay_status = (data.get("pay_status") or "").lower()
        if pay_status in ("successful", "success", "completed"):
            tx._set_done()
        elif pay_status in ("failed", "declined"):
            tx._set_error("Payment failed.")
        elif pay_status in ("cancelled", "canceled"):
            tx._set_canceled()
        else:
            tx._set_error(f"Unexpected status: {pay_status}")

        return http.Response("OK", status=200)
