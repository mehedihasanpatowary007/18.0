from odoo.tools import SQL
from odoo import models, fields, api, tools

class InheritProductCategories(models.Model):
    _inherit = 'product.public.category'
    
    is_available_homepage = fields.Boolean(
        string="Available on Homepage",
        default=False,
        help="Display this category on homepage"
    )