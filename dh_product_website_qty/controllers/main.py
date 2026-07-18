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

from odoo.addons.sale.controllers.product_configurator import SaleProductConfiguratorController
from odoo.http import Controller, request, route
	
def _get_product_information(
	self,
	product_template,
	combination,
	currency,
	pricelist,
	so_date,
	quantity=1,
	product_uom_id=None,
	parent_combination=None,
	**kwargs,
):
	""" Return complete information about a product.

	:param product.template product_template: The product for which to seek information.
	:param product.template.attribute.value combination: The combination of the product.
	:param res.currency currency: The currency of the transaction.
	:param product.pricelist pricelist: The pricelist to use.
	:param datetime so_date: The date of the `sale.order`, to compute the price at the right
		rate.
	:param int quantity: The quantity of the product.
	:param int|None product_uom_id: The unit of measure of the product, as a `uom.uom` id.
	:param product.template.attribute.value|None parent_combination: The combination of the
		parent product.
	:param dict kwargs: Locally unused data passed to `_get_basic_product_information`.
	:rtype: dict
	:return: A dict with the following structure:
		{
			'product_tmpl_id': int,
			'id': int,
			'description_sale': str|False,
			'display_name': str,
			'price': float,
			'quantity': int
			'attribute_line': [{
				'id': int
				'attribute': {
					'id': int
					'name': str
					'display_type': str
				},
				'attribute_value': [{
					'id': int,
					'name': str,
					'price_extra': float,
					'html_color': str|False,
					'image': str|False,
					'is_custom': bool
				}],
				'selected_attribute_id': int,
			}],
			'exclusions': dict,
			'archived_combination': dict,
			'parent_exclusions': dict,
		}
	"""
	product_uom = request.env['uom.uom'].browse(product_uom_id)
	product = product_template._get_variant_for_combination(combination)
	attribute_exclusions = product_template._get_attribute_exclusions(
		parent_combination=parent_combination,
		combination_ids=combination.ids,
	)
	product_or_template = product or product_template

	if product_or_template.display_product_qty_limits:
		quantity = product_or_template.minimum_product_quantity
	else:
		quantity = 1

	values = dict(
		product_tmpl_id=product_template.id,
		**self._get_basic_product_information(
			product_or_template,
			pricelist,
			combination,
			quantity=quantity,
			uom=product_uom,
			currency=currency,
			date=so_date,
			**kwargs,
		),
		quantity=quantity,
		attribute_lines=[dict(
			id=ptal.id,
			attribute=dict(**ptal.attribute_id.read(['id', 'name', 'display_type'])[0]),
			attribute_values=[
				dict(
					**ptav.read(['name', 'html_color', 'image', 'is_custom'])[0],
					price_extra=self._get_ptav_price_extra(
						ptav, currency, so_date, product_or_template
					),
				) for ptav in ptal.product_template_value_ids
				if ptav.ptav_active or combination and ptav.id in combination.ids
			],
			selected_attribute_value_ids=combination.filtered(
				lambda c: ptal in c.attribute_line_id
			).ids,
			create_variant=ptal.attribute_id.create_variant,
		) for ptal in product_template.attribute_line_ids],
		exclusions=attribute_exclusions['exclusions'],
		archived_combinations=attribute_exclusions['archived_combinations'],
		parent_exclusions=attribute_exclusions['parent_exclusions'],
	)
	# Shouldn't be sent client-side
	values.pop('pricelist_rule_id', None)
	return values

SaleProductConfiguratorController._get_product_information = _get_product_information