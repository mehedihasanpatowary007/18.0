from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Count all variants of the same product template in the cart.
    def _website_cart_template_quantity(self):
        self.ensure_one()
        return sum(
            self.order_id.website_order_line.filtered(
                lambda line: line.product_id.product_tmpl_id == self.product_id.product_tmpl_id
                and not line.is_delivery
            ).mapped("product_uom_qty")
        )

    def _website_cart_limit_reached(self):
        self.ensure_one()
        limit = self.product_id.product_tmpl_id.website_max_cart_qty
        return bool(limit and self._website_cart_template_quantity() >= limit)

    def _website_cart_limit_warning(self):
        self.ensure_one()
        if not self.product_id.product_tmpl_id.website_max_cart_qty:
            return ""
        return self.order_id._get_website_cart_limit_message(self.product_id)
