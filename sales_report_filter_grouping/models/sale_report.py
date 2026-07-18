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

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Additional filtering fields
    report_category = fields.Selection([
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('online', 'Online'),
        ('direct', 'Direct Sales'),
        ('other', 'Other'),
    ], string='Report Category', help='Category for sales reporting and filtering')

    priority_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority Level', default='medium', help='Priority level for order processing')

    # Grouping fields
    pos_config_id = fields.Many2one(
        'pos.config',
        string='Point of Sale',
        help='Link this sale order to a specific Point of Sale configuration'
    )

    sales_region = fields.Selection([
        ('central', 'Central'),
        ('international', 'International'),
    ], string='Sales Region', help='Geographic region for sales grouping')

    customer_segment = fields.Selection([
        ('new', 'New Customer'),
        ('regular', 'Regular Customer'),
        ('vip', 'VIP Customer'),
        ('inactive', 'Inactive Customer'),
    ], string='Customer Segment', compute='_compute_customer_segment', store=True,
        help='Customer segment based on purchase history')

    # Status tracking fields
    payment_status = fields.Selection([
        ('pending', 'Payment Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
    ], string='Payment Status', compute='_compute_payment_status', store=True,
        help='Current payment status of the order')

    delivery_status = fields.Selection([
        ('not_shipped', 'Not Shipped'),
        ('partial', 'Partially Shipped'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ], string='Delivery Status', compute='_compute_delivery_status', store=True,
        help='Current delivery status of the order')

    order_progress = fields.Float(
        string='Order Progress (%)',
        compute='_compute_order_progress',
        store=True,
        help='Overall progress of the order completion'
    )

    # Analytics fields
    days_to_confirm = fields.Integer(
        string='Days to Confirm',
        compute='_compute_days_to_confirm',
        store=True,
        help='Number of days taken to confirm the order'
    )

    order_age = fields.Integer(
        string='Order Age (Days)',
        compute='_compute_order_age',
        help='Number of days since order creation'
    )

    # Comprehensive status combining sale + delivery + payment
    overall_status = fields.Selection([
        ('draft', 'Draft - Pending'),
        ('pending_payment', 'Confirmed - Pending Payment'),
        ('pending_delivery', 'Paid - Pending Delivery'),
        ('partial_delivery', 'Paid - Partial Delivery'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], string='Overall Status', compute='_compute_overall_status', store=True,
        help='Comprehensive status combining sale state, payment, and delivery status')

    # Vape Status: Quotation → Sales Order → Send to Courier → Done (Delivered)
    vape_status = fields.Selection([
        ('quotation', 'Quotation'),
        ('sales_order', 'Sales Order'),
        ('send_to_courier', 'Send to Courier'),
        ('done', 'Done (Delivered)'),
        ('cancelled', 'Cancelled'),
    ], string='Vape Status', compute='_compute_vape_status', store=True,
        help='Workflow status: Quotation → Sales Order → Send to Courier → Done (Delivered)')

    @api.depends('partner_id', 'partner_id.sale_order_count')
    def _compute_customer_segment(self):
        """Compute customer segment based on order history"""
        for order in self:
            if order.partner_id:
                order_count = order.partner_id.sale_order_count
                if order_count <= 1:
                    order.customer_segment = 'new'
                elif order_count <= 5:
                    order.customer_segment = 'regular'
                elif order_count > 5:
                    order.customer_segment = 'vip'
                else:
                    order.customer_segment = 'inactive'
            else:
                order.customer_segment = 'new'

    @api.depends('invoice_status', 'invoice_ids', 'invoice_ids.payment_state')
    def _compute_payment_status(self):
        """Compute payment status based on invoices"""
        for order in self:
            if not order.invoice_ids:
                order.payment_status = 'pending'
            else:
                payment_states = order.invoice_ids.mapped('payment_state')
                if all(state == 'paid' for state in payment_states):
                    order.payment_status = 'paid'
                elif any(state == 'paid' for state in payment_states):
                    order.payment_status = 'partial'
                elif any(state == 'overdue' for state in payment_states if state):
                    order.payment_status = 'overdue'
                else:
                    order.payment_status = 'pending'

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_delivery_status(self):
        """Compute delivery status based on pickings"""
        for order in self:
            if not order.picking_ids:
                order.delivery_status = 'not_shipped'
            else:
                picking_states = order.picking_ids.mapped('state')
                if all(state == 'done' for state in picking_states):
                    order.delivery_status = 'delivered'
                elif any(state == 'done' for state in picking_states):
                    order.delivery_status = 'partial'
                elif any(state in ['assigned', 'confirmed'] for state in picking_states):
                    order.delivery_status = 'shipped'
                else:
                    order.delivery_status = 'not_shipped'

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_order_progress(self):
        """Compute overall order progress"""
        for order in self:
            if not order.picking_ids:
                order.order_progress = 0.0
            else:
                total_pickings = len(order.picking_ids)
                done_pickings = len(order.picking_ids.filtered(lambda p: p.state == 'done'))
                if total_pickings > 0:
                    order.order_progress = (done_pickings / total_pickings) * 100
                else:
                    order.order_progress = 0.0

    @api.depends('create_date', 'date_order')
    def _compute_days_to_confirm(self):
        """Compute days taken to confirm the order"""
        for order in self:
            if order.create_date and order.date_order:
                delta = order.date_order.date() - order.create_date.date()
                order.days_to_confirm = delta.days
            else:
                order.days_to_confirm = 0

    @api.depends('create_date')
    def _compute_order_age(self):
        """Compute order age in days"""
        for order in self:
            if order.create_date:
                delta = fields.Date.today() - order.create_date.date()
                order.order_age = delta.days
            else:
                order.order_age = 0

    @api.depends('state', 'payment_status', 'delivery_status')
    def _compute_overall_status(self):
        """Compute comprehensive status combining sale, payment, and delivery status"""
        for order in self:
            # Cancelled orders
            if order.state == 'cancel':
                order.overall_status = 'cancelled'
            # Draft/Quote orders
            elif order.state in ['draft', 'sent']:
                order.overall_status = 'draft'
            # Overdue orders
            elif order.payment_status == 'overdue':
                order.overall_status = 'overdue'
            # Completed orders (Paid + Delivered)
            elif order.payment_status == 'paid' and order.delivery_status == 'delivered':
                order.overall_status = 'completed'
            # Partial delivery
            elif order.payment_status == 'paid' and order.delivery_status == 'partial':
                order.overall_status = 'partial_delivery'
            # Pending delivery (Paid but not shipped/delivered)
            elif order.payment_status == 'paid' and order.delivery_status in ['not_shipped', 'shipped']:
                order.overall_status = 'pending_delivery'
            # Pending payment (Confirmed but not paid)
            elif order.state == 'sale' and order.payment_status in ['pending', 'partial']:
                order.overall_status = 'pending_payment'
            # In progress (everything else that's active)
            elif order.state == 'sale':
                order.overall_status = 'in_progress'
            else:
                order.overall_status = 'draft'

    @api.depends('state', 'delivery_status', 'picking_ids', 'picking_ids.state')
    def _compute_vape_status(self):
        """Compute vape status: Quotation → Sales Order → Send to Courier → Done (Delivered)

        Integrates with delivery_courier_custom module:
        - Checks for 'courier_assigned' state in stock.picking
        """
        for order in self:
            # Cancelled orders
            if order.state == 'cancel':
                order.vape_status = 'cancelled'
            # Quotation (Draft/Sent state)
            elif order.state in ['draft', 'sent']:
                order.vape_status = 'quotation'
            # Confirmed orders - check picking states for workflow progression
            elif order.state == 'sale':
                if not order.picking_ids:
                    # No pickings yet - Sales Order
                    order.vape_status = 'sales_order'
                else:
                    picking_states = order.picking_ids.mapped('state')

                    # Done (Delivered) - All pickings are done
                    if all(state == 'done' for state in picking_states):
                        order.vape_status = 'done'
                    # Send to Courier - Any picking is courier_assigned or in transit
                    elif any(state == 'courier_assigned' for state in picking_states):
                        order.vape_status = 'send_to_courier'
                    elif any(state in ['assigned', 'confirmed'] for state in picking_states):
                        # Ready or confirmed pickings - still Sales Order stage
                        order.vape_status = 'sales_order'
                    else:
                        # Default to Sales Order
                        order.vape_status = 'sales_order'
            else:
                order.vape_status = 'quotation'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], string='Line Status', default='pending',
        help='Status of individual order line')

    fulfillment_progress = fields.Float(
        string='Fulfillment Progress (%)',
        compute='_compute_fulfillment_progress',
        store=True,
        help='Percentage of line item fulfilled'
    )

    @api.depends('qty_delivered', 'product_uom_qty')
    def _compute_fulfillment_progress(self):
        """Compute fulfillment progress for order line"""
        for line in self:
            if line.product_uom_qty > 0:
                line.fulfillment_progress = (line.qty_delivered / line.product_uom_qty) * 100
            else:
                line.fulfillment_progress = 0.0




class SaleReport(models.Model):
    """Add vape_status and pos_config_id to Sales Analysis Report (Sales > Reporting > Sales)"""
    _inherit = 'sale.report'

    pos_config_id = fields.Many2one('pos.config', string='Point of Sale', readonly=True)
    pos_name = fields.Char(string='POS Name', readonly=True)

    vape_status = fields.Selection([
        ('quotation', 'Quotation'),
        ('sales_order', 'Sales Order'),
        ('send_to_courier', 'Send to Courier'),
        ('done', 'Done (Delivered)'),
        ('cancelled', 'Cancelled'),
    ], string='Vape Status', readonly=True)

    cost_price = fields.Float(string='Cost Price', compute='_compute_cost_price', readonly=True)

    @api.depends('product_id')
    def _compute_cost_price(self):
        """Compute cost price from product standard price"""
        for record in self:
            record.cost_price = record.product_id.standard_price if record.product_id else 0.0

    def _select_sale(self):
        """Add pos_config_id, pos_name and vape_status to SELECT clause for sale orders"""
        select_str = super()._select_sale()
        select_str += """,
            s.pos_config_id as pos_config_id,
            (SELECT name FROM pos_config WHERE id = s.pos_config_id) as pos_name,
            s.vape_status as vape_status"""
        return select_str

    def _select_pos(self):
        """Add pos_config_id, pos_name and vape_status to SELECT clause for POS orders"""
        select_str = super()._select_pos()
        select_str += """,
            pos.config_id as pos_config_id,
            (SELECT name FROM pos_config WHERE id = pos.config_id) as pos_name,
            NULL as vape_status"""
        return select_str

    def _group_by_sale(self):
        """Add pos_config_id and vape_status to GROUP BY clause for sale orders"""
        group_by_str = super()._group_by_sale()
        group_by_str += """,
            s.pos_config_id,
            s.vape_status"""
        return group_by_str

    def _group_by_pos(self):
        """Add pos_config_id to GROUP BY clause for POS orders"""
        group_by_str = super()._group_by_pos()
        group_by_str += """,
            pos.config_id"""
        return group_by_str

    def init(self):
        """Force recreation of the SQL view to include our custom fields"""
        super().init()