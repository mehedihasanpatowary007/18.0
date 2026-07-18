# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class payment_aamar_pay(models.Model):
#     _name = 'payment_aamar_pay.payment_aamar_pay'
#     _description = 'payment_aamar_pay.payment_aamar_pay'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

