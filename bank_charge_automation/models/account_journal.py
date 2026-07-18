from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    has_bank_fees = fields.Boolean(string="Has Bank Fees?")
    bank_charge_amount = fields.Float(string="Bank Charge Amount(%)", digits=(16, 2))
    bank_charge_account_id = fields.Many2one(
        'account.account',
        string="Bank Charge Account",
        domain=[('account_type', '=', 'expense')],
        help="Account to record bank service charges."
    )

