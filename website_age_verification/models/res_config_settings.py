# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Texts
    age_title = fields.Char(
        string="Title",
        config_parameter='age.title',
        default="Verify your age to proceed"
    )
    age_message = fields.Char(
        string="Message",
        config_parameter='age.message',
        default="Please verify that you are of legal age to access this content"
    )
    age_message_sub = fields.Char(
        string="Sub Message",
        config_parameter='age.message_sub',
        default="By entering our website, you affirm that you are of legal smoking age in your jurisdiction and you agree to be Age Verified."
    )
    age_fallback_url = fields.Char(
        string="Fallback URL",
        config_parameter='age.fallback_url',
        default="https://www.google.com"
    )

    # Style (simplified -> SOLID colours)
    age_title_bg = fields.Char(
        string="Popup Title Background",
        config_parameter='age.title_bg',
        default="#4da3ff"
    )
    age_main_bg = fields.Char(
        string="Main Popup Background",
        config_parameter='age.main_bg',
        default="#2b2b2b"
    )
    age_yes_bg = fields.Char(
        string="Yes Button Background",
        config_parameter='age.yes_bg',
        default="#27ae60"
    )
    age_no_bg = fields.Char(
        string="No Button Background",
        config_parameter='age.no_bg',
        default="#c0392b"
    )
    age_text_color = fields.Char(
        string="Popup Text Color",
        config_parameter='age.text_color',
        default="#ffffff"
    )

    # Logo field - stored as attachment
    age_logo = fields.Binary(
        string="Popup Logo",
        attachment=True,
        help="Logo to display in the age verification popup (recommended size: 200x200px)"
    )
    age_logo_filename = fields.Char(string="Logo Filename")

    @api.model
    def get_values(self):
        """Load values from ir.config_parameter"""
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        # Get logo attachment ID
        logo_attachment_id = params.get_param('age.logo.attachment_id', default=False)
        logo_data = False
        logo_filename = False
        logo_url = False

        if logo_attachment_id:
            try:
                attachment = self.env['ir.attachment'].sudo().browse(int(logo_attachment_id))
                if attachment.exists():
                    logo_data = attachment.datas
                    logo_filename = attachment.name
                    logo_url = '/web/content/%s' % attachment.id
            except Exception:
                _logger.exception("Failed to read logo attachment")

        res.update({
            'age_title': params.get_param('age.title', default="Verify your age to proceed"),
            'age_message': params.get_param('age.message', default="Please verify that you are of legal age to access this content"),
            'age_message_sub': params.get_param('age.message_sub', default=""),
            'age_fallback_url': params.get_param('age.fallback_url', default="https://www.google.com"),

            'age_title_bg': params.get_param('age.title_bg', default="#4da3ff"),
            'age_main_bg': params.get_param('age.main_bg', default="#2b2b2b"),
            'age_yes_bg': params.get_param('age.yes_bg', default="#27ae60"),
            'age_no_bg': params.get_param('age.no_bg', default="#c0392b"),
            'age_text_color': params.get_param('age.text_color', default="#ffffff"),

            'age_logo': logo_data,
            'age_logo_filename': logo_filename,
        })
        return res

    def set_values(self):
        """Save values to ir.config_parameter"""
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()

        # Save text parameters
        params.set_param('age.title', self.age_title or "")
        params.set_param('age.message', self.age_message or "")
        params.set_param('age.message_sub', self.age_message_sub or "")
        params.set_param('age.fallback_url', self.age_fallback_url or "")

        # Save style params
        params.set_param('age.title_bg', self.age_title_bg or "#4da3ff")
        params.set_param('age.main_bg', self.age_main_bg or "#2b2b2b")
        params.set_param('age.yes_bg', self.age_yes_bg or "#27ae60")
        params.set_param('age.no_bg', self.age_no_bg or "#c0392b")
        params.set_param('age.text_color', self.age_text_color or "#ffffff")

        # Handle logo attachment
        if self.age_logo:
            # Delete old attachment if exists
            old_attachment_id = params.get_param('age.logo.attachment_id', default=False)
            if old_attachment_id:
                try:
                    old_attachment = self.env['ir.attachment'].sudo().browse(int(old_attachment_id))
                    if old_attachment.exists():
                        old_attachment.unlink()
                except Exception:
                    _logger.exception("Failed to remove old attachment")

            # Detect mimetype from filename
            filename = (self.age_logo_filename or 'age_verification_logo.png')
            mimetype = 'image/png'
            if filename.lower().endswith(('.jpg', '.jpeg')):
                mimetype = 'image/jpeg'
            elif filename.lower().endswith('.gif'):
                mimetype = 'image/gif'
            elif filename.lower().endswith('.svg'):
                mimetype = 'image/svg+xml'
            elif filename.lower().endswith('.webp'):
                mimetype = 'image/webp'

            # Create new attachment
            try:
                attachment = self.env['ir.attachment'].sudo().create({
                    'name': filename,
                    'type': 'binary',
                    'datas': self.age_logo,
                    'res_model': 'res.config.settings',
                    'res_field': 'age_logo',
                    'res_id': 0,
                    'public': True,
                    'mimetype': mimetype,
                })
                params.set_param('age.logo.attachment_id', attachment.id)
            except Exception:
                _logger.exception("Failed to create logo attachment")
        elif self.age_logo == False:
            # Remove logo if deleted
            old_attachment_id = params.get_param('age.logo.attachment_id', default=False)
            if old_attachment_id:
                try:
                    old_attachment = self.env['ir.attachment'].sudo().browse(int(old_attachment_id))
                    if old_attachment.exists():
                        old_attachment.unlink()
                except Exception:
                    _logger.exception("Failed to delete attachment")
                params.set_param('age.logo.attachment_id', False)
