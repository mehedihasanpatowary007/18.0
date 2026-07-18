# -*- coding: utf-8 -*-
###############################################################################
#
#    Datahat Solutions LLP
#
#    Copyright (C) 2023-TODAY Datahat Solutions LLP (<https://www.datahatsolutions.com>)
#    Author: Datahat Solutions LLP (info@datahatcs.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api,fields,models

class ProductTemplate(models.Model):
	_inherit = 'product.template'
	

	minimum_product_quantity = fields.Integer(
		string='Minimum Quantity',
		help='Defines the minimum quantity allowed when adding the product to the cart.'
	)
	maximum_product_quantity = fields.Integer(
		string='Maximum Quantity',
		help='Defines the maximum quantity allowed when adding the product to the cart.'
	)
	product_quantity_multipler = fields.Integer(
		string='Quantity Multiplier',
		help='Defines the step size by which the product quantity increases or decreases when changing the quantity.'
	)
	display_product_qty_limits = fields.Boolean(
		string='Limit Cart Quantity',
		help='Enable this option to enforce minimum, maximum, and step quantity limits when a customer adds the product to the cart.'
	)




class ProductProduct(models.Model):
	_inherit = 'product.product'


	def _get_max_quantity(self, website, **kwargs):
		""" The max quantity of a product is the difference between the quantity that's free to use
		and the quantity that's already been added to the cart.

		Note: self.ensure_one()

		:param website website: The website for which to compute the max quantity.
		:return: The max quantity of the product.
		:rtype: float | None
		"""
		self.ensure_one()
		if self.is_storable and not self.allow_out_of_stock_order:
			free_qty = website._get_product_available_qty(self.sudo(), **kwargs)
			cart_qty = self._get_cart_qty(website)
			if self.product_tmpl_id.maximum_product_quantity > free_qty:
				return free_qty - cart_qty
			elif self.product_tmpl_id.maximum_product_quantity < free_qty:
				return self.product_tmpl_id.maximum_product_quantity - cart_qty
			else:
				return free_qty - cart_qty
		return None

