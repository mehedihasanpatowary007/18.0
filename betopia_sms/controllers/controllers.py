# -*- coding: utf-8 -*-
# from odoo import http


# class BetopiaSms(http.Controller):
#     @http.route('/betopia_sms/betopia_sms', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/betopia_sms/betopia_sms/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('betopia_sms.listing', {
#             'root': '/betopia_sms/betopia_sms',
#             'objects': http.request.env['betopia_sms.betopia_sms'].search([]),
#         })

#     @http.route('/betopia_sms/betopia_sms/objects/<model("betopia_sms.betopia_sms"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('betopia_sms.object', {
#             'object': obj
#         })

