from odoo import _
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCartLimit(WebsiteSale):
    def _check_cart_and_addresses(self, order_sudo):
        if order_sudo:
            errors = order_sudo._get_website_cart_limit_errors()
            if errors:
                order_sudo.shop_warning = errors[0]
                return request.redirect("/shop/cart")
        return super()._check_cart_and_addresses(order_sudo)

    def _get_shop_payment_errors(self, order):
        errors = super()._get_shop_payment_errors(order)
        if order:
            for error in order._get_website_cart_limit_errors():
                errors.append((_("Maximum Limit Reached"), error))
        return errors
