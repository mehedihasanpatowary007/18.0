from odoo import fields, models


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
