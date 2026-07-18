# -*- coding: utf-8 -*-

from . import models
from . import controllers
from odoo.tools.sql import column_exists
from odoo.exceptions import UserError
from odoo.service import common


def pre_init_check(env):
    # Check if pyotp is installed
    try:
        import pyotp
    except ImportError as e:
        raise UserError(
            "Installation Error: {} => Kindly install https://pypi.python.org/pypi/pyotp".format(e)
        )

    # Check Odoo server version
    version_info = common.exp_version()
    server_serie = version_info.get("server_serie")
    if server_serie != "18.0":
        raise UserError(
            "Module supports Odoo series 18.0, found {}.".format(server_serie)
        )

    # Add 'otp_varified' column if it doesn't exist
    if not column_exists(env.cr, "res_partner", "otp_varified"):
        env.cr.execute("""
            ALTER TABLE "res_partner"
            ADD COLUMN "otp_varified" bool
        """)
