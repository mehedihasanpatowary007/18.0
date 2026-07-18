# -*- coding: utf-8 -*-
import re
import logging
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.service import security
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS = {
    'db', 'debug', 'token', 'message', 'error', 'scope', 'mode',
    'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
    'password', 'confirm_password', 'city', 'signup_email'
}

class MetaAuthSignupHome(Home):

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def checkExistingUser(self, **kwargs):
        login = kwargs.get('login') or kwargs.get('mobile') or kwargs.get('email')
        if not login:
            return False, [0, _("Please provide valid Login Email or Mobile Number."), 0]

        user_obj = request.env['res.users'].sudo().search([
            '|', ('login', '=', login), ('mobile', '=', login)
        ], limit=1)

        if not user_obj:
            return False, [0, _("No user is found registered using this email or mobile number."), 0]

        return user_obj, [1, _("User found."), 0]

    def normalize_otp_response(self, otp_msg):
        """
        Ensure OTP response is always dict with keys: status, msg, resp(optional)
        """

        if isinstance(otp_msg, dict):
            status = otp_msg.get("status", "error")
            message = otp_msg.get("msg", "")
        elif isinstance(otp_msg, (list, tuple)):
            status = "success" if otp_msg[0] else "error"
            message = otp_msg[1] if len(otp_msg) > 1 else ""
        else:
            status = "error"
            message = "Unexpected OTP response format"
        return {"status": status, "msg": message}


    @http.route(website=True, auth="public", sitemap=False,csrf=False)

    def web_login(self, redirect=None, *args, **kw):
        signin_auth = request.env['ir.default'].sudo()._get('res.config.settings', 'signin_auth')
        if not signin_auth:
            return super().web_login(redirect=redirect, *args, **kw)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}

        try:
            values['databases'] = http.db_list()
        except:
            values['databases'] = None

        values['redirect'] = redirect or '/web'
        render_template = 'meta_otp_auth.login'
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if request.httprequest.method == 'POST':
            login = request.params.get('login')
            values['login'] = login
            if request.params.get('login_with_pass'):

                values['auth_type'] = 'password'
                return request.render('meta_otp_auth.login_auth_password', values)

            if request.params.get('login_with_otp') or request.params.get('resend_otp'):

                user_data, msg = self.checkExistingUser(**kw)

                if user_data and msg[0] == 1:
                    if self.is_valid_email(login):
                        otp_msg = user_data.partner_id.send_otp()
                    else:
                        otp_msg = user_data.partner_id.send_sms_otp()

                        _logger.info("OTP Message: %s", otp_msg)

                    otp_resp = self.normalize_otp_response(otp_msg)

                    if otp_resp["status"] == "error":
                        values['error'] = otp_resp["msg"]
                    else:
                        values['message'] = otp_resp["msg"]

                    return request.render("meta_otp_auth.login_auth_otp", values)
                else:
                    values['error'] = msg[1] if len(msg) > 1 else "User not found"
                    return request.render("meta_otp_auth.login", values)

            try:

                auth_type = request.params.get("auth_type")

                if request.params.get("auth_type") =="password":

                    credential = {'login': request.params['login'],'password': request.params['password'],'type': 'password'}
                    uid = request.session.authenticate(request.db, credential)
                    uid = uid.get("uid")

                elif auth_type == "otp":
                    otp_rec = request.env['meta.otp.auth'].sudo().search([
                        ('partner_id.email', '=', login),
                        ('otp', '=', request.params["password"])
                    ], limit=1)
                    if otp_rec:
                        otp_rec = otp_rec
                    else:
                        otp_rec = request.env['meta.otp.auth'].sudo().search([
                            ('partner_id.mobile', '=', login),
                            ('otp', '=', request.params["password"])

                            ], limit=1)

                    if otp_rec:
                        user = request.env['res.users'].sudo().search([('partner_id', '=', otp_rec.partner_id.id)], limit=1)

                        if user:
                            request.session.uid = user.id
                            request.session.session_token = security.compute_session_token(request.session, request.env)
                            uid = user.id

                if not uid:
                    raise AccessDenied("Wrong login/password or OTP")

                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))

            except AccessDenied as e:
                if request.params.get('auth_type') == 'otp':
                    values['error'] = _("Wrong OTP")
                    render_template = 'meta_otp_auth.login_auth_otp'
                else:
                    values['error'] = _("Wrong login/password")
                    render_template = 'meta_otp_auth.login_auth_password'

            except Exception as e:
                values['error'] = "Wrong OTP"


        response = request.render(render_template, values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    # @http.route(['/otp/verification'], type='http', auth="public", website=True)

    # def otp_verification(self, redirect=None):
    #     partner = request.env.user.partner_id
    #     if not partner:
    #         return request.redirect('/web/login')
    #     resp = partner.send_otp()
    #     redirect = redirect or '/my'
    #     return request.render('meta_otp_auth.otp_verify_after_signup', {'partner': partner, 'resp': resp, 'redirect': redirect})

    # @http.route(['/otp/verify'], type='http', auth="public", methods=['POST'], website=True)
    # def verify_otp(self, redirect=None, **post):
    #     totp = post.get('otpin')
    #     partner_id = int(post.get('partner_id'))
    #     partner = request.env.user.partner_id

    #     resp = request.env['meta.otp.auth'].verify_otp(partner_id, totp)
    #     redirect = redirect or '/my'
    #     if resp[0] and partner_id == partner.id:
    #         return request.redirect(redirect)
    #     else:
    #         return request.render('meta_otp_auth.otp_verify_after_signup', {'partner': partner, 'resp': resp, 'redirect': redirect})

# class OtpAuthWebsiteSale(WebsiteSale):
#     @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
#     def checkout(self, **post):
#         partner = request.env.user.partner_id
#         if partner.is_public:
#             return request.redirect("/web")
#         if not partner.otp_varified:
#             return request.redirect("/otp/verification?redirect=/shop/checkout")
#         return super(OtpAuthWebsiteSale, self).checkout()
