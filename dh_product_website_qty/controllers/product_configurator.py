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

from odoo.http import Controller, request, route


class SaleProductGetValue(Controller):

	@route(route='/sale/product/get_values', type='json', auth='user')
	def sale_product_get_values(
		self,
		product_template_id,
		**kwargs,
	):
		product_template = request.env['product.template'].browse(product_template_id)
		return {
			'display_product_qty_limits': product_template.display_product_qty_limits,
			'minimum_product_quantity': product_template.minimum_product_quantity,
			'maximum_product_quantity': product_template.maximum_product_quantity,
			'product_quantity_multipler': product_template.product_quantity_multipler,
		}
