from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_invoice_lines_values(self, line_values, pos_order_line):
        values = super()._get_invoice_lines_values(line_values, pos_order_line)
        values["pos_fixed_discount_amount"] = pos_order_line._get_fixed_discount_for_quantity(
            line_values["quantity"]
        )
        return values
