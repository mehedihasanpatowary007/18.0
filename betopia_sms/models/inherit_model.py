from odoo import models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    """Inheriting purchase order for including SMS functions"""
    _inherit = 'purchase.order'

    def action_purchase_sms(self):
        """Open SMS wizard and log message on the chatter"""
        self.ensure_one()  # Make sure it's only one order at a time

        # Post a log message in the chatter
        self.message_post(body="SMS sent via Adn.")

        # Open the SMS wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Message Content'),
            'res_model': 'sms.builder',   # this must be a real model in your DB
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name':self.name,
                'default_partner_id': self.partner_id.id,
                'default_purchase_id': self.id,  # optional, in case your wizard needs the PO
            },
            'views': [(False, 'form')],
        }


class SaleOrder(models.Model):
    """Inheriting purchase order for including SMS functions"""
    _inherit = 'sale.order'

    def action_sale_sms(self):
        """Open SMS wizard and log message on the chatter"""
        self.ensure_one()  # Make sure it's only one order at a time

        # Post a log message in the chatter
        self.message_post(body=f"SMS sent via Adn.")

        # Open the SMS wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Message Content'),
            'res_model': 'sms.builder',   # this must be a real model in your DB
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name':self.name,
                'default_partner_id': self.partner_id.id,
                'default_sale_id': self.id,

            },
            'views': [(False, 'form')],
        }


class AccountMove(models.Model):
    """Inheriting purchase order for including SMS functions"""
    _inherit = 'account.move'

    def action_invoice_sms(self):
        """Open SMS wizard and log message on the chatter"""
        self.ensure_one()  # Make sure it's only one order at a time

        # Post a log message in the chatter
        self.message_post(body="SMS sent via Adn.")

        # Open the SMS wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Message Content'),
            'res_model': 'sms.builder',   # this must be a real model in your DB
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name':self.name,
                'default_partner_id': self.partner_id.id,
                'default_invoice_id': self.id,  # optional, in case your wizard needs the PO
            },
            'views': [(False, 'form')],
        }



class AccountPayment(models.Model):
    """Inheriting purchase order for including SMS functions"""
    _inherit = 'account.payment'

    def action_payment_sms(self):
        """Open SMS wizard and log message on the chatter"""
        self.ensure_one()  # Make sure it's only one order at a time

        # Post a log message in the chatter
        self.message_post(body="SMS sent viaAdn.")

        # Open the SMS wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Message Content'),
            'res_model': 'sms.builder',   # this must be a real model in your DB
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name':self.name,
                'default_partner_id': self.partner_id.id,
                'default_payment_id': self.id,  # optional, in case your wizard needs the PO
            },
            'views': [(False, 'form')],
        }
