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

{
	'name': 'Product Cart Quantity Control',
	'version': '18.0.1.0.1',
	'category': 'Product',
	'author':'Datahat Solutions LLP',
    'company': 'Datahat Solutions LLP, India',
    'price': 20,
    'currency': 'EUR',
    'license': 'LGPL-3',
    'summary':"""
                This module allows you to manage product quantity restrictions on your Odoo E-commerce website with precision and flexibility. 
                You can configure Minimum Quantity, Maximum Quantity, and Quantity Multiplier for each product. These rules work together to ensure 
                that customers can only purchase products in valid quantities as per your business requirements.
		Odoo website product quantity restriction, Odoo eCommerce min max quantity, Odoo set minimum order quantity, Odoo maximum quantity per order website, Odoo product quantity multiplier, Odoo product purchase limit website, Odoo quantity control for webshop, Odoo website product quantity rules, Odoo bulk sales quantity limit, Odoo enforce minimum purchase quantity, Odoo restrict product quantity website, Odoo sales quantity increment setting, Odoo webshop quantity step, Odoo website product min max step, Odoo ecommerce order quantity management, Odoo restrict over-ordering website, Odoo website inventory control module, Odoo product quantity limit for customers, Odoo quantity validation ecommerce, Odoo webshop quantity configuration, Odoo stepwise quantity control website, Odoo website minimum purchase rule, Odoo ecommerce quantity workflow, Odoo sales multiplier webshop, Product order control Odoo ecommerce
  		Odoo website product quantity restriction, Odoo e-commerce minimum order quantity, Odoo maximum quantity per order website, Odoo quantity multiplier for products, Odoo bulk sales quantity management, Odoo product purchase limits website, Odoo enforce minimum purchase quantity, Odoo set maximum order quantity, Odoo quantity increments product sales, Odoo e-commerce order quantity control, Product quantity rules Odoo website, Odoo webshop quantity validation, Odoo website restrict order quantity, Odoo sales quantity multiplier setup, Odoo quantity step product configuration, Odoo product quantity constraints website, Odoo online store bulk order management, Odoo e-commerce quantity enforcement, Odoo website multiple quantity control, Odoo webshop product quantity rules, Odoo minimum maximum quantity module, Odoo webshop inventory quantity restriction, Odoo website purchase quantity settings, Odoo sales order quantity restriction, Odoo product increments enforcement website.
    		Website Quantity Min Max And Multiplier
            """,
    'description': """
    				This module enhances your Odoo E-commerce website by enabling precise control over product quantity restrictions. 
    				You can define Minimum Quantity, Maximum Quantity, and Quantity Multiplier for each product individually. 
    				These settings work together to ensure that customers can only purchase products in specific, valid quantities—helping 
    				you enforce bulk sales, avoid under- or over-ordering, and meet packaging or inventory requirements.

    				Key Features:

    					Effortless Bulk Sales Management: Set Minimum Product Quantities
							Enhance your sales strategy by easily defining minimum order quantities for your products. Perfect for wholesale operations or enforcing purchase limits, 
							this feature simplifies bulk sales by allowing you to configure minimum quantity requirements with ease.

						Simplified Order Limits: Set Maximum Product Quantity
							Easily customize your sales process by defining maximum order quantities for products that require purchase limits. 
							This intuitive feature helps maintain order accuracy and supports efficient inventory management.

						Accurate Ordering Made Easy: Set Product Quantity Multiples
							Maintain precise order quantities by configuring a Quantity Multiplier for products that must be purchased in specific increments. 
							This feature allows you to seamlessly align your sales process with unique product requirements.

						Unified Quantity Control: Minimum, Maximum & Multiplier Working in Sync
							Gain complete control over product orders with seamlessly integrated Minimum, Maximum, and Multiplier settings. 
							Ensure accurate quantity management and enjoy a smooth, efficient sales workflow.
    				""",
	'depends': [
				'sale',
				'product',
				'website_sale_stock',
			],
	'live_test_url': 'https://apps.datahatsolutions.com/apps/app/18.0/dh_product_website_qty',
	'website': 'https://apps.datahatsolutions.com/apps/app/18.0/dh_product_website_qty',
	'images': ['static/description/banner.gif'],
	'data': [
		'views/product_template_inherit_view.xml',
		'views/templates.xml',
	],
	'assets': {
        'web.assets_frontend': [
        	'/dh_product_website_qty/static/src/js/product_quantity_change.js',
        	'/dh_product_website_qty/static/src/js/product_configurator_dialog.js',
        	'/dh_product_website_qty/static/src/xml/product_configurator_dialog.xml',
        	'/dh_product_website_qty/static/src/js/product_list.js',
        	'/dh_product_website_qty/static/src/xml/productlist.xml',
        	'/dh_product_website_qty/static/src/js/product.js',
        	'/dh_product_website_qty/static/src/xml/product.xml',
        	'/dh_product_website_qty/static/src/js/quantity_button.js',
        	'/dh_product_website_qty/static/src/xml/quantity_button.xml',
        	'/dh_product_website_qty/static/src/js/combo_configurator_dialog.js',
        	'/dh_product_website_qty/static/src/xml/combo_configuaor_dialog.xml',
        	'/dh_product_website_qty/static/src/js/website_sale.js',
        ],
    },
	'installable': True,
	'application': False,
	'auto_install': False,
}
