# -*- coding: utf-8 -*-

import email
from odoo import http, _
from odoo.http import request, route
from odoo import http
import pyotp
import requests
import base64
import json
from odoo.exceptions import ValidationError, UserError


import logging

_logger=logging.getLogger(__name__)

from odoo.addons.portal.controllers.portal import CustomerPortal
# from odoo.addons.auth_signup.models.res_users import SignupError

# class OTPCustomerPortal(CustomerPortal):

#     @route(['/my', '/my/home'], type='http', auth="user", website=True)
#     def home(self, **kw):
#         """
#         Override for default Home route
#         """
#         partner = request.env.user.partner_id
#         if (partner.email or (partner.phone or partner.mobile)) and not partner.otp_varified:
#             return request.redirect('/my/account')
#         return super(OTPCustomerPortal, self).home()

    # @route(['/my/account'], type='http', auth='user', website=True)
    # def account(self, redirect=None, **post):
    #     self = super(OTPCustomerPortal, self)
    #     values = self._prepare_portal_layout_values()
    #     user = request.env.user
    #     partner = user.partner_id
    #     phone = partner.phone
    #     email = partner.email
    #     values.update({
    #         'error': {},
    #         'error_message': [],
    #     })

    #     if post and request.httprequest.method == 'POST':
    #         error, error_message = self.details_form_validate(post)
    #         values.update({'error': error, 'error_message': error_message})
    #         values.update(post)
    #         if not error:
    #             values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
    #             values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
    #             for field in set(['country_id', 'state_id']) & set(values.keys()):
    #                 try:
    #                     values[field] = int(values[field])
    #                 except:
    #                     values[field] = False
    #             values.update({'zip': values.pop('zipcode', '')})
    #             otp_varified = partner.otp_varified
    #             if (values.get('email') and values['email'] != email)\
    #                 or (values.get('phone') and values['phone'] != phone):
    #                 otp_varified = False
    #                 user.sudo().write({
    #                     "login":values.get('email', user.login),
    #                     "mobile":values.get('phone', user.mobile),
    #                 })

    #                 values.update({"otp_varified":otp_varified})

    #             _logger.warning("Portal my account values to update {}".format(values))


    #             partner.sudo().write(values)
    #             if redirect:
    #                 return request.redirect(redirect)
    #             return request.redirect('/my/home')

        # countries = request.env['res.country'].sudo().search([])
        # states = request.env['res.country.state'].sudo().search([])

        # values.update({
        #     'partner': partner,
        #     'countries': countries,
        #     'states': states,
        #     'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
        #     'redirect': redirect,
        #     'page_name': 'my_details',
        # })

        # response = request.render("portal.portal_my_details", values)
        # response.headers['X-Frame-Options'] = 'DENY'
        # return response

