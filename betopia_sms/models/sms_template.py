# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from markupsafe import Markup
from odoo import api, fields, models, _
from odoo.tools import plaintext2html

class BetopiaSMSTemplate(models.Model):
    _name = 'betopia.sms.template'
    _description = 'Betopia SMS Templates'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name', required=True)
    sms_account = fields.Many2one('betopia.sms.account', string='SMS Account', required=True)
    footer_text = fields.Char(string='Footer Message')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')], default='draft', string='Status', tracking=True)
    messages_count = fields.Integer(string="Messages Count", compute='_compute_messages_count')
    body = fields.Text(string='SMS Body')


    def action_open_messages(self):
        self.ensure_one()
        return {
            'name': _("Message Statistics Of %(template_name)s", template_name=self.name),
            'view_mode': 'list,form,graph',
            'res_model': 'betopia.sms.message',
            'domain': [('betopia_sms_template_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_posted(self):
        return self.write({'state': 'posted'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})


    def _compute_messages_count(self):
        for template in self:
            template.messages_count = self.env['betopia.sms.message'].sudo().search_count([
                ('template_id','=',template.id)
            ])
