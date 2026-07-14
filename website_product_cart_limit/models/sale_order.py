from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Message shown when the customer tries to exceed the configured limit.
    def _get_website_cart_limit_message(self, product, cart_qty=0):
        limit = product.product_tmpl_id.website_max_cart_qty
        if cart_qty:
            return _(
                "Maximum Limit Reached: You already have %(cart_qty)s in your cart. "
                "You can buy a total of %(limit)s units only.",
                cart_qty=int(cart_qty),
                limit=int(limit),
            )
        return _(
            "Maximum Limit Reached: You can only add up to %(limit)s units of this product.",
            limit=int(limit),
        )

    # Validate the full website cart before checkout and payment.
    def _get_website_cart_limit_errors(self):
        self.ensure_one()
        errors = []
        grouped_qty = {}
        for line in self.website_order_line.filtered(lambda line: line.product_id and not line.is_delivery):
            template = line.product_id.product_tmpl_id
            if not template.website_max_cart_qty:
                continue
            grouped_qty.setdefault(template, 0)
            grouped_qty[template] += line.product_uom_qty
        for template, quantity in grouped_qty.items():
            if quantity > template.website_max_cart_qty:
                errors.append(
                    _(
                        "Maximum Limit Reached: You can only add up to %(limit)s units of %(product)s.",
                        limit=int(template.website_max_cart_qty),
                        product=template.display_name,
                    )
                )
        return errors

    # Odoo calls this hook for product-page adds and cart quantity changes.
    def _verify_updated_quantity(self, order_line, product_id, new_qty, **kwargs):
        verified_qty, warning = super()._verify_updated_quantity(
            order_line, product_id, new_qty, **kwargs
        )
        product = self.env["product.product"].browse(product_id).exists()
        limit = product.product_tmpl_id.website_max_cart_qty if product else 0
        if not product or not limit or verified_qty <= 0:
            return verified_qty, warning

        other_qty = sum(
            self.website_order_line.filtered(
                lambda line: line.product_id.product_tmpl_id == product.product_tmpl_id
                and line.id != order_line.id
                and not line.is_delivery
            ).mapped("product_uom_qty")
        )
        allowed_qty = max(limit - other_qty, 0)
        if verified_qty > allowed_qty:
            verified_qty = allowed_qty
            warning = self._get_website_cart_limit_message(product, other_qty)
        return verified_qty, warning
