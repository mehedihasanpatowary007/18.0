# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Override state field to add custom Courier Assigned state in correct order
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting'),
            ('assigned', 'Ready'),
            ('courier_assigned', 'Courier Assigned'),  # Custom state before 'done'
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        copy=False,
        default='draft',
        tracking=True,
        help="Status of the transfer"
    )

    # courier_id field removed - delivery.courier model no longer exists
    courier_name = fields.Char(string='Courier Name', tracking=True)
    courier_phone = fields.Char(string='Courier Phone', tracking=True)
    courier_sent_date = fields.Datetime(string='Courier Sent Date', readonly=True, copy=False)
    courier_delivered_date = fields.Datetime(string='Delivered Date', readonly=True, copy=False)
    courier_notes = fields.Text(string='Courier Notes')
    show_send_courier = fields.Boolean(compute='_compute_show_buttons', string='Show Send Courier')
    show_mark_delivered = fields.Boolean(compute='_compute_show_buttons', string='Show Mark Delivered')

    @api.depends('state')
    def _compute_show_buttons(self):
        """Compute visibility of courier action buttons"""
        for picking in self:
            # Show Send Courier button only when state is 'assigned' (Ready)
            # Hide when Done, Cancelled, or any other state
            picking.show_send_courier = (
                picking.state == 'assigned'
            )
            # Show Mark as Delivered button only when state is 'courier_assigned'
            # Hide when Done, Cancelled, or any other state
            picking.show_mark_delivered = (
                picking.state == 'courier_assigned'
            )

    def button_validate(self):
        """Override to automatically update delivery date when picking is validated"""
        res = super(StockPicking, self).button_validate()
        for picking in self:
            # Automatically update delivered date when picking is done from courier_assigned state
            if picking.state == 'done' and picking.courier_sent_date:
                picking._auto_update_courier_delivered()
        return res

    def _action_done(self):
        """Override to automatically update delivery date when picking is done"""
        res = super(StockPicking, self)._action_done()
        for picking in self:
            # Automatically update delivered date when picking is done
            if picking.state == 'done' and picking.courier_sent_date:
                picking._auto_update_courier_delivered()
        return res

    def _auto_update_courier_delivered(self):
        """Helper method to automatically update courier delivered date"""
        self.ensure_one()
        if self.state == 'done' and not self.courier_delivered_date:
            self.write({
                'courier_delivered_date': fields.Datetime.now(),
            })
            # Post automatic delivery completion message
            message = _(
                'Delivery Completed (Automatic)'
                'Delivered on: %s'
            ) % (
                fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            self.message_post(
                body=message,
                subject='Delivery Completed',
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

    def action_send_courier(self):
        """Send delivery to courier and notify via email"""
        self.ensure_one()

        # Carrier field is now optional - no validation required
        # if not self.carrier_id and not self.courier_id:
        #     raise UserError(_('Please select a courier or delivery method before sending.'))

        # Update main state to courier_assigned
        self.write({
            'state': 'courier_assigned',
            'courier_sent_date': fields.Datetime.now(),
        })

        # Flush changes to database to ensure state is saved
        self.flush_model()

        # Post message in chatter
        try:
            self._post_courier_message()
        except Exception as e:
            # Log error but don't fail the operation
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Failed to post courier message: {str(e)}")

        # Send email notification
        try:
            self._send_courier_email()
        except Exception as e:
            # Log error but don't fail the operation
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Failed to send courier email: {str(e)}")

        # Return True to trigger automatic UI update without reload
        return True

    def action_mark_delivered(self):
        """Mark delivery as delivered by courier (manual override)
        Note: Status automatically updates to 'Done' when picking is validated.
        This button is for manual override if needed.
        """
        self.ensure_one()

        if self.state != 'courier_assigned':
            raise UserError(_('Can only mark deliveries that have been sent to courier.'))

        # Update state to done
        self.write({
            'courier_delivered_date': fields.Datetime.now(),
        })

        # Post message in chatter
        message = _(
            'Delivery Completed (Manual)'
            'Delivered on: %s'
        ) % (
            fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self.message_post(
            body=message,
            subject='Delivery Completed',
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )

        # Validate the picking if not already done
        if self.state != 'done':
            self.button_validate()

        # Return True to trigger automatic UI update without reload
        return True

    def _post_courier_message(self):
        """Post formatted message in chatter when courier is sent"""
        self.ensure_one()

        import logging
        _logger = logging.getLogger(__name__)

        try:
            # Build simplified message
            message_lines = ['Delivery Sent']
            message_lines.append('')

            # Delivery information
            message_lines.append('Delivery Order: %s' % self.name)
            message_lines.append('Customer: %s' % (self.partner_id.name or 'N/A'))
            message_lines.append('Delivery Address:%s' % (self._get_formatted_address() or 'N/A'))

            # Delivery method only (no courier details)
            if self.carrier_id:
                message_lines.append(' Delivery Method: %s' % self.carrier_id.name)

            # Products summary
            message_lines.append('Products:')
            message_lines.append('')
            for move in self.move_ids:
                message_lines.append(
                    '%s - Qty: %s %s' % (
                        move.product_id.name,
                        move.product_uom_qty,
                        move.product_uom.name
                    )
                )
            message_lines.append('')

            # Send date
            message_lines.append('Sent Date: %s' % fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            if self.courier_notes:
                message_lines.append('Notes:%s' % self.courier_notes)

            message = ''.join(message_lines)

            # Post message to chatter (HTML will be rendered automatically)
            self.message_post(
                body=message,
                subject='Courier Assigned',
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

            _logger.info(f"Courier message posted successfully for {self.name}")

        except Exception as e:
            _logger.error(f"Error posting courier message for {self.name}: {str(e)}")
            raise

    def _send_courier_email(self):
        """Send email notification when courier is assigned"""
        self.ensure_one()

        import logging
        _logger = logging.getLogger(__name__)

        # Check if partner has email
        if not self.partner_id or not self.partner_id.email:
            _logger.warning(f"Cannot send courier email for {self.name}: Partner has no email address")
            return

        # Get email template
        template = self.env.ref('delivery_courier_custom.email_template_courier_assignment', raise_if_not_found=False)
        if not template:
            _logger.error(f"Email template 'delivery_courier_custom.email_template_courier_assignment' not found")
            return

        # Send email
        try:
            # Generate the rendered email content
            email_values = template.generate_email(self.id)

            # Send the email with force_send to ensure immediate sending
            template.send_mail(
                self.id,
                force_send=True,
                email_values={
                    'email_to': self.partner_id.email,
                    'body_html': email_values.get('body_html'),  # Use rendered body
                    'subject': email_values.get('subject'),  # Use rendered subject
                },
                notif_layout='mail.mail_notification_light'
            )
            _logger.info(f"Courier email sent successfully for {self.name} to {self.partner_id.email}")
        except Exception as e:
            _logger.error(f"Failed to send courier email for {self.name}: {str(e)}")

    def _get_formatted_address(self):
        """Get formatted delivery address"""
        self.ensure_one()
        partner = self.partner_id
        address_parts = []

        if partner.street:
            address_parts.append(partner.street)
        if partner.street2:
            address_parts.append(partner.street2)
        if partner.city:
            address_parts.append(partner.city)
        if partner.state_id:
            address_parts.append(partner.state_id.name)
        if partner.zip:
            address_parts.append(partner.zip)
        if partner.country_id:
            address_parts.append(partner.country_id.name)

        return ', '.join(address_parts) if address_parts else False

