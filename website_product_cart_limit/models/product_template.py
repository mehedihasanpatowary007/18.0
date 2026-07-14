from odoo import fields, models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_max_cart_qty = fields.Integer(
        string="Maximum Cart Quantity",
        default=0,
        help=(
            "Maximum number of units a customer can add to their website cart "
            "for this product. Leave empty or 0 for no limit."
        ),
    )

    # Current website cart quantity for this product template.
    def _get_website_cart_qty(self):
        self.ensure_one()
        try:
            order = request.website.sale_get_order()
        except RuntimeError:
            return 0
        if not order:
            return 0
        return sum(
            order.website_order_line.filtered(
                lambda line: line.product_id.product_tmpl_id == self and not line.is_delivery
            ).mapped("product_uom_qty")
        )
