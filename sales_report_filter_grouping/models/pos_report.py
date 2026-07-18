# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

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
    sales_region = fields.Selection([
        ('central', 'Central'),
        ('international', 'International'),
    ], string='Sales Region', help='Geographic region for sales grouping')

    customer_segment = fields.Selection([
        ('new', 'New Customer'),
        ('regular', 'Regular Customer'),
        ('vip', 'VIP Customer'),
        ('walk_in', 'Walk-in Customer'),
    ], string='Customer Segment', compute='_compute_customer_segment', store=True,
        help='Customer segment based on purchase history')

    # Status tracking fields
    payment_status = fields.Selection([
        ('pending', 'Payment Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    ], string='Payment Status', compute='_compute_payment_status', store=True,
        help='Current payment status of the order')

    order_age = fields.Integer(
        string='Order Age (Days)',
        compute='_compute_order_age',
        help='Number of days since order creation'
    )

    # Session and shift tracking
    session_state = fields.Selection(
        related='session_id.state',
        string='Session State',
        store=True,
        help='Current state of the POS session'
    )

    # Analytics fields
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_profit_margin',
        store=True,
        help='Profit margin percentage for the order'
    )

    avg_items_per_order = fields.Float(
        string='Average Items',
        compute='_compute_avg_items',
        help='Average number of items per order'
    )

    @api.depends('partner_id')
    def _compute_customer_segment(self):
        """Compute customer segment based on order history"""
        for order in self:
            if order.partner_id:
                # Count previous orders for this customer
                order_count = self.search_count([
                    ('partner_id', '=', order.partner_id.id),
                    ('state', 'in', ['paid', 'done', 'invoiced'])
                ])
                if order_count <= 1:
                    order.customer_segment = 'new'
                elif order_count <= 5:
                    order.customer_segment = 'regular'
                elif order_count > 5:
                    order.customer_segment = 'vip'
                else:
                    order.customer_segment = 'walk_in'
            else:
                order.customer_segment = 'walk_in'

    @api.depends('payment_ids', 'payment_ids.amount', 'amount_total')
    def _compute_payment_status(self):
        """Compute payment status based on payments"""
        for order in self:
            if not order.payment_ids:
                order.payment_status = 'pending'
            else:
                total_paid = sum(order.payment_ids.mapped('amount'))
                if total_paid >= order.amount_total:
                    order.payment_status = 'paid'
                elif total_paid > 0:
                    order.payment_status = 'partial'
                else:
                    order.payment_status = 'pending'

    @api.depends('date_order')
    def _compute_order_age(self):
        """Compute order age in days"""
        for order in self:
            if order.date_order:
                delta = fields.Date.today() - order.date_order.date()
                order.order_age = delta.days
            else:
                order.order_age = 0

    @api.depends('margin', 'amount_total')
    def _compute_profit_margin(self):
        """Compute profit margin percentage"""
        for order in self:
            if order.amount_total > 0:
                order.profit_margin = (order.margin / order.amount_total) * 100
            else:
                order.profit_margin = 0.0

    @api.depends('lines')
    def _compute_avg_items(self):
        """Compute average items per order"""
        for order in self:
            if order.lines:
                order.avg_items_per_order = len(order.lines)
            else:
                order.avg_items_per_order = 0.0


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    line_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], string='Line Status', default='completed',
        help='Status of individual order line')

    discount_amount = fields.Float(
        string='Discount Amount',
        compute='_compute_discount_amount',
        store=True,
        help='Total discount amount for this line'
    )

    @api.depends('price_unit', 'qty', 'discount')
    def _compute_discount_amount(self):
        """Compute discount amount"""
        for line in self:
            if line.discount > 0:
                line.discount_amount = (line.price_unit * line.qty * line.discount) / 100
            else:
                line.discount_amount = 0.0
