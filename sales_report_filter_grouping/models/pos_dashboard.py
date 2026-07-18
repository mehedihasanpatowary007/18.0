# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class PosDashboard(models.Model):
    _name = 'pos.dashboard'
    _description = 'POS Dashboard Statistics'

    name = fields.Char(string='Dashboard Name', default='POS Dashboard')
    date_from = fields.Date(string='Date From', default=lambda self: fields.Date.today())
    date_to = fields.Date(string='Date To', default=lambda self: fields.Date.today())

    # Summary Statistics
    total_orders = fields.Integer(string='Total Orders', compute='_compute_statistics')
    total_revenue = fields.Monetary(string='Total Revenue', compute='_compute_statistics')
    average_order_value = fields.Monetary(string='Average Order Value', compute='_compute_statistics')
    total_margin = fields.Monetary(string='Total Margin', compute='_compute_statistics')
    profit_margin_percentage = fields.Float(string='Profit Margin %', compute='_compute_statistics')

    # Payment Statistics
    paid_orders = fields.Integer(string='Paid Orders', compute='_compute_payment_stats')
    pending_orders = fields.Integer(string='Pending Orders', compute='_compute_payment_stats')
    partial_payment_orders = fields.Integer(string='Partial Payment', compute='_compute_payment_stats')

    # Customer Statistics
    total_customers = fields.Integer(string='Total Customers', compute='_compute_customer_stats')
    new_customers = fields.Integer(string='New Customers', compute='_compute_customer_stats')
    vip_customers = fields.Integer(string='VIP Customers', compute='_compute_customer_stats')
    regular_customers = fields.Integer(string='Regular Customers', compute='_compute_customer_stats')

    # Category Statistics
    retail_orders = fields.Integer(string='Retail Orders', compute='_compute_category_stats')
    wholesale_orders = fields.Integer(string='Wholesale Orders', compute='_compute_category_stats')
    online_orders = fields.Integer(string='Online Orders', compute='_compute_category_stats')
    direct_orders = fields.Integer(string='Direct Sales', compute='_compute_category_stats')

    # Session Statistics
    active_sessions = fields.Integer(string='Active Sessions', compute='_compute_session_stats')
    closed_sessions = fields.Integer(string='Closed Sessions', compute='_compute_session_stats')

    # Region Statistics
    central_sales = fields.Monetary(string='Central Sales', compute='_compute_region_stats')
    international_sales = fields.Monetary(string='International Sales', compute='_compute_region_stats')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')

    @api.depends('date_from', 'date_to')
    def _compute_statistics(self):
        """Compute main dashboard statistics"""
        for dashboard in self:
            domain = [
                ('date_order', '>=', dashboard.date_from),
                ('date_order', '<=', dashboard.date_to),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ]

            orders = self.env['pos.order'].search(domain)

            dashboard.total_orders = len(orders)
            dashboard.total_revenue = sum(orders.mapped('amount_total'))
            dashboard.total_margin = sum(orders.mapped('margin'))
            dashboard.average_order_value = dashboard.total_revenue / dashboard.total_orders if dashboard.total_orders > 0 else 0
            dashboard.profit_margin_percentage = (dashboard.total_margin / dashboard.total_revenue * 100) if dashboard.total_revenue > 0 else 0

    @api.depends('date_from', 'date_to')
    def _compute_payment_stats(self):
        """Compute payment statistics"""
        for dashboard in self:
            domain = [
                ('date_order', '>=', dashboard.date_from),
                ('date_order', '<=', dashboard.date_to),
            ]

            dashboard.paid_orders = self.env['pos.order'].search_count(domain + [('payment_status', '=', 'paid')])
            dashboard.pending_orders = self.env['pos.order'].search_count(domain + [('payment_status', '=', 'pending')])
            dashboard.partial_payment_orders = self.env['pos.order'].search_count(domain + [('payment_status', '=', 'partial')])

    @api.depends('date_from', 'date_to')
    def _compute_customer_stats(self):
        """Compute customer statistics"""
        for dashboard in self:
            domain = [
                ('date_order', '>=', dashboard.date_from),
                ('date_order', '<=', dashboard.date_to),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ]

            orders = self.env['pos.order'].search(domain)
            dashboard.total_customers = len(orders.mapped('partner_id'))
            dashboard.new_customers = len(orders.filtered(lambda o: o.customer_segment == 'new'))
            dashboard.vip_customers = len(orders.filtered(lambda o: o.customer_segment == 'vip'))
            dashboard.regular_customers = len(orders.filtered(lambda o: o.customer_segment == 'regular'))

    @api.depends('date_from', 'date_to')
    def _compute_category_stats(self):
        """Compute category statistics"""
        for dashboard in self:
            domain = [
                ('date_order', '>=', dashboard.date_from),
                ('date_order', '<=', dashboard.date_to),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ]

            dashboard.retail_orders = self.env['pos.order'].search_count(domain + [('report_category', '=', 'retail')])
            dashboard.wholesale_orders = self.env['pos.order'].search_count(domain + [('report_category', '=', 'wholesale')])
            dashboard.online_orders = self.env['pos.order'].search_count(domain + [('report_category', '=', 'online')])
            dashboard.direct_orders = self.env['pos.order'].search_count(domain + [('report_category', '=', 'direct')])

    @api.depends('date_from', 'date_to')
    def _compute_session_stats(self):
        """Compute session statistics"""
        for dashboard in self:
            domain = [
                ('start_at', '>=', fields.Datetime.to_datetime(dashboard.date_from)),
                ('start_at', '<=', fields.Datetime.to_datetime(dashboard.date_to)),
            ]

            dashboard.active_sessions = self.env['pos.session'].search_count(domain + [('state', '=', 'opened')])
            dashboard.closed_sessions = self.env['pos.session'].search_count(domain + [('state', '=', 'closed')])

    @api.depends('date_from', 'date_to')
    def _compute_region_stats(self):
        """Compute regional sales statistics"""
        for dashboard in self:
            domain = [
                ('date_order', '>=', dashboard.date_from),
                ('date_order', '<=', dashboard.date_to),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ]

            central_orders = self.env['pos.order'].search(domain + [('sales_region', '=', 'central')])
            international_orders = self.env['pos.order'].search(domain + [('sales_region', '=', 'international')])

            dashboard.central_sales = sum(central_orders.mapped('amount_total'))
            dashboard.international_sales = sum(international_orders.mapped('amount_total'))

    def action_view_orders(self):
        """Open POS orders view"""
        return {
            'name': 'POS Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'list,form,kanban',
            'domain': [
                ('date_order', '>=', self.date_from),
                ('date_order', '<=', self.date_to),
            ],
            'context': {'create': False}
        }

    def action_view_paid_orders(self):
        """Open paid POS orders"""
        return {
            'name': 'Paid Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'list,form',
            'domain': [
                ('date_order', '>=', self.date_from),
                ('date_order', '<=', self.date_to),
                ('payment_status', '=', 'paid'),
            ],
            'context': {'create': False}
        }

    def action_view_pending_orders(self):
        """Open pending POS orders"""
        return {
            'name': 'Pending Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'list,form',
            'domain': [
                ('date_order', '>=', self.date_from),
                ('date_order', '<=', self.date_to),
                ('payment_status', '=', 'pending'),
            ],
            'context': {'create': False}
        }
