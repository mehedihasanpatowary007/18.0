# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Soaeb Abdullah
#    Company: BD calling IT Limited
#    Maintainer: Soaeb Abdullah
#    Version: 17.0.1.0.0
#    Website: https://soaeb.odoo.com/
#
##############################################################################
{
    'name': 'Sales Report Filter Grouping & Status',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Enhanced sales and POS reporting with advanced filtering, grouping, and status management @ Soaeb Abdullah',
    'description': """
        Sales Report Filter Grouping & Status
        ======================================
        This module enhances the sales and POS reporting functionality with:
        * Advanced filtering options for sales orders and POS orders
        * Custom grouping capabilities
        * Vape Status: Workflow tracking (Quotation → Sales Order → Send to Courier → Done)
        * Overall Status: Comprehensive status combining sale, payment, and delivery
        * Status tracking and management
        * Enhanced sales and POS analysis views
        * Better data organization and reporting
        * POS report analysis with pivot and graph views
        * Customer segmentation for both sales and POS
        * Product Cost Price in Sales Analysis Report
        * Cost-based profitability analysis

        Integration:
        * Integrates with delivery_courier_custom module for courier tracking
        * Automatically detects courier_assigned state in deliveries
        * Works standalone or with courier module

        Merged Modules:
        * Includes functionality from sale_cost_report module
    """,
    'author': 'Soaeb Abdullah',
    'website': 'BD calling IT Limited',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'point_of_sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/assign_pos_to_orders.xml',
        'views/sale_report_views.xml',
        'views/sale_report_tree_view.xml',
        'views/sale_order_views.xml',
        'views/pos_report_views.xml',
        'views/pos_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
