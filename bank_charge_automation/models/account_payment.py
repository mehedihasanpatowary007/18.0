import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    has_bank_fees = fields.Boolean(
        string="Has Bank Fees?",
        related='journal_id.has_bank_fees',
        store=True,
        readonly=True
    )
    bank_charge_amount = fields.Float(
        string="Bank Charge Amount",
        related='journal_id.bank_charge_amount',
        store=True,
        readonly=True
    )
    bank_charge_account_id = fields.Many2one(
        'account.account',
        string="Bank Charge Account",
        related='journal_id.bank_charge_account_id',
        readonly=True
    )
    bank_charge_total = fields.Monetary(
        string="Bank Charge Total",
        compute="_compute_bank_charge_total",
        store=True,
        readonly=True,
        currency_field="currency_id"
    )
    net_amount = fields.Monetary(
        string="Net Amount",
        compute="_compute_net_amount",
        store=True,
        readonly=True,
        currency_field="currency_id"
    )
    processed = fields.Boolean(
        string="Processed",
        compute="_compute_processed",
        store=True
    )

    @api.depends('journal_id')
    def _compute_processed(self):
        for payment in self:
            payment.processed = bool(
                payment.journal_id.has_bank_fees and payment.journal_id.type == 'bank'
            )

    @api.depends('amount', 'bank_charge_amount', 'has_bank_fees')
    def _compute_bank_charge_total(self):
        for payment in self:
            if payment.has_bank_fees and payment.bank_charge_amount:
                payment.bank_charge_total = (payment.amount * payment.bank_charge_amount) / 100.0
            else:
                payment.bank_charge_total = 0.0

    @api.depends('amount', 'bank_charge_total')
    def _compute_net_amount(self):
        for payment in self:
            payment.net_amount = payment.amount - payment.bank_charge_total

    def _create_bank_charge_line(self, move, payment, bank_charge):
        """Create a balanced bank charge line depending on payment type."""
        if not payment.bank_charge_account_id:
            raise UserError(_("Please configure a Bank Charge Account in the Journal."))

        # Determine debit/credit depending on payment type
        line_vals = {
            'name': _("Bank Charge - %s") % payment.name,
            'account_id': payment.bank_charge_account_id.id,
            'move_id': move.id,
            'journal_id': payment.journal_id.id,
            'partner_id': False,
            'debit': bank_charge if payment.payment_type == 'inbound' else 0.0,
            'credit': bank_charge if payment.payment_type == 'outbound' else 0.0,
        }
        line = self.env['account.move.line'].create(line_vals)
        _logger.info("✅ [BankCharge] Bank charge line created: %s (%.2f)", line.id, bank_charge)
        return line

    def action_post(self):
        """Post payment, handle bank charges, adjust bank line, reconcile invoices."""
        _logger.info("🔹 [BankCharge] Posting payment(s) %s", self.ids)

        # 1️⃣ Post payment normally (super handles move creation/posting)
        res = super(AccountPayment, self).action_post()

        for payment in self:
            if not payment.has_bank_fees or payment.bank_charge_amount <= 0:
                continue

            move = payment.move_id
            if not move:
                _logger.warning("⚠️ [BankCharge] No journal move found for payment %s.", payment.name)
                continue

            bank_charge = round((payment.amount * payment.bank_charge_amount) / 100.0, 2)
            _logger.info("💰 [BankCharge] %.2f%% of %.2f = %.2f", payment.bank_charge_amount, payment.amount, bank_charge)

            try:
                # 2️⃣ Adjust bank line
                bank_line = move.line_ids.filtered(
                    lambda l: l.account_id == payment.journal_id.default_account_id and (
                        (payment.payment_type == 'inbound' and l.debit > 0) or
                        (payment.payment_type == 'outbound' and l.credit > 0)
                    )
                )[:1]

                if bank_line:
                    if payment.payment_type == 'inbound':
                        new_debit = round(bank_line.debit - bank_charge, 2)
                        if new_debit < 0:
                            raise UserError(_("Bank line cannot go negative after deduction."))
                        bank_line.write({'debit': new_debit})
                    else:
                        new_credit = round(bank_line.credit - bank_charge, 2)
                        if new_credit < 0:
                            raise UserError(_("Bank line cannot go negative after deduction."))
                        bank_line.write({'credit': new_credit})

                # 3️⃣ Create balanced bank charge line
                self._create_bank_charge_line(move, payment, bank_charge)

                # 4️⃣ Ensure move is posted
                if move.state != 'posted':
                    move.action_post()

                # 5️⃣ Reconcile payment line with invoice lines if any
                for inv in payment.invoice_ids:
                    receivable_account = (
                        payment.partner_id.property_account_receivable_id
                        if payment.payment_type == 'inbound'
                        else payment.partner_id.property_account_payable_id
                    )
                    for inv_line in inv.line_ids.filtered(lambda l: l.account_id == receivable_account):
                        if bank_line and not inv_line.reconciled:
                            (inv_line + bank_line).reconcile()
                            _logger.info("✅ [BankCharge] Reconciled invoice line %s with payment line %s",
                                         inv_line.id, bank_line.id)

                    # Update invoice payment state
                    inv._compute_outstanding_credits_debits()
                    inv._compute_outstanding_credits_credits()
                    inv._recompute_payment_state()
                    _logger.info("✅ [BankCharge] Updated invoice %s credits and payment state.", inv.name)

            except Exception as e:
                _logger.exception("❌ [BankCharge] Failed to apply bank charge for payment %s: %s", payment.name, e)
                # Ensure bank charge line exists even if error occurred
                self._create_bank_charge_line(move, payment, bank_charge)

        return res
