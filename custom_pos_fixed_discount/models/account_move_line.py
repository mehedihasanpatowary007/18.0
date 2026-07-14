from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools import frozendict


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pos_fixed_discount_amount = fields.Monetary(
        string="POS Fixed Discount",
        currency_field="currency_id",
        copy=False,
        help="Fixed discount amount coming from a POS order line.",
    )

    @api.depends(
        "account_id",
        "company_id",
        "discount",
        "price_unit",
        "quantity",
        "currency_rate",
        "analytic_distribution",
        "pos_fixed_discount_amount",
    )
    def _compute_discount_allocation_needed(self):
        super()._compute_discount_allocation_needed()

        fixed_discount_lines = {
            line: line._get_fixed_discount_allocation_amounts()
            for line in self.move_id.line_ids
            if line.display_type == "product"
            and line.pos_fixed_discount_amount
            and (discount_allocation_account := line.move_id._get_discount_allocation_account())
            and line.account_id != discount_allocation_account
            and line.currency_id.round(line.move_id.direction_sign * line.pos_fixed_discount_amount)
        }

        distribution_totals = defaultdict(lambda: defaultdict(float))
        for line, discounted_amounts in fixed_discount_lines.items():
            for account, _amount_currency, amount in discounted_amounts:
                for analytic_account_id in line.analytic_distribution or {}:
                    distribution_totals[frozendict({
                        "move_id": line.move_id.id,
                        "account_id": account.id,
                        "currency_rate": line.currency_rate,
                    })][analytic_account_id] += amount

        for line in self:
            if line not in fixed_discount_lines:
                continue

            line.discount_allocation_dirty = True
            discount_allocation_needed = dict(line.discount_allocation_needed or {})
            for account, amount_currency, amount in fixed_discount_lines[line]:
                key = frozendict({
                    "move_id": line.move_id.id,
                    "account_id": account.id,
                    "currency_rate": line.currency_rate,
                })
                dist = distribution_totals[key]
                total = sum(dist.values()) or 1
                analytic_distribution = {
                    account_id: 100 * value / total
                    for account_id, value in dist.items()
                }
                existing_vals = dict(discount_allocation_needed.get(key, {}))
                discount_allocation_needed[key] = frozendict({
                    "display_type": "discount",
                    "name": existing_vals.get("name", _("Discount")),
                    "amount_currency": existing_vals.get("amount_currency", 0.0) + amount_currency,
                    "balance": existing_vals.get("balance", 0.0) + amount,
                    "analytic_distribution": existing_vals.get(
                        "analytic_distribution",
                        analytic_distribution,
                    ),
                })
            line.discount_allocation_needed = discount_allocation_needed

    def _get_fixed_discount_allocation_amounts(self):
        self.ensure_one()
        discount_allocation_account = self.move_id._get_discount_allocation_account()
        amount_currency = self.currency_id.round(
            self.move_id.direction_sign * self.pos_fixed_discount_amount
        )
        amount = self.company_currency_id.round(amount_currency / (self.currency_rate or 1.0))
        return [
            (self.account_id, amount_currency, amount),
            (discount_allocation_account, -amount_currency, -amount),
        ]
