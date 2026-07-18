from . import controllers
from . import models
from .aamar_pay.payment import AamarPay   # Import your AamarPay SDK wrapper

from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(env):
    """Register AamarPay as a payment provider when the module is installed."""
    setup_provider(env, 'aamar_pay')


def uninstall_hook(env):
    """Unregister AamarPay when the module is uninstalled."""
    reset_payment_provider(env, 'aamar_pay')
