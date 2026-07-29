from collections import defaultdict

from odoo import models, _
from odoo.tools import float_is_zero


class PosSession(models.Model):
    _inherit = "pos.session"

    def _accumulate_amounts(self, data):
        data = super()._accumulate_amounts(data)
        discount_account = self.company_id.account_discount_expense_allocation_id
        fixed_discount_allocations = defaultdict(lambda: {"amount": 0.0, "amount_converted": 0.0})

        if discount_account:
            for order in self._get_closed_orders().filtered(lambda pos_order: not pos_order.is_invoiced):
                for base_line in order.with_context(linked_to_pos=True)._prepare_tax_base_line_values():
                    order_line = base_line["record"]
                    amount = order_line._get_fixed_discount_allocation_amount_currency(
                        base_line.get("quantity", order_line.qty)
                    )
                    if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                        continue

                    fixed_discount_allocations[base_line["account_id"].id] = self._update_amounts(
                        fixed_discount_allocations[base_line["account_id"].id],
                        {"amount": amount},
                        order.date_order,
                    )
                    fixed_discount_allocations[discount_account.id] = self._update_amounts(
                        fixed_discount_allocations[discount_account.id],
                        {"amount": -amount},
                        order.date_order,
                    )

        data["fixed_discount_allocations"] = fixed_discount_allocations
        return data

    def _create_non_reconciliable_move_lines(self, data):
        data = super()._create_non_reconciliable_move_lines(data)
        fixed_discount_allocations = data.get("fixed_discount_allocations") or {}
        discount_vals = [
            self._get_fixed_discount_allocation_vals(
                account_id,
                amounts["amount"],
                amounts["amount_converted"],
            )
            for account_id, amounts in fixed_discount_allocations.items()
            if not float_is_zero(amounts["amount"], precision_rounding=self.currency_id.rounding)
            or not float_is_zero(
                amounts["amount_converted"],
                precision_rounding=self.company_id.currency_id.rounding,
            )
        ]
        if discount_vals:
            data["MoveLine"].create(discount_vals)
        return data

    def _get_fixed_discount_allocation_vals(self, account_id, amount, amount_converted):
        return {
            "name": _("Discount"),
            "account_id": account_id,
            "move_id": self.move_id.id,
            "display_type": "discount",
            "currency_id": self.currency_id.id,
            "amount_currency": amount,
            "balance": amount_converted,
        }
