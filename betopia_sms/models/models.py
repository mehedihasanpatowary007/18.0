# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class betopia_sms(models.Model):
#     _name = 'betopia_sms.betopia_sms'
#     _description = 'betopia_sms.betopia_sms'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

