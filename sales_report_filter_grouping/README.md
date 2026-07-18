# Sales Report Filter Grouping & Status

## Overview
This module enhances Odoo's sales reporting functionality with advanced filtering, grouping, and status management capabilities.

## Features

### 1. Advanced Filtering Options
- **Report Category**: Categorize sales orders (Retail, Wholesale, Online, Direct Sales, Other)
- **Priority Level**: Set priority levels (Low, Medium, High, Urgent)
- **Sales Region**: Track sales by geographic regions (North, South, East, West, Central, International)
- **Customer Segment**: Automatic segmentation (New, Regular, VIP, Inactive)

### 2. Enhanced Status Tracking
- **Vape Status**: Workflow tracking from quote to delivery (Quotation → Sales Order → Send to Courier → Done (Delivered))
  - Integrates with `delivery_courier_custom` module
  - Automatically detects when delivery is assigned to courier
  - Updates status when courier state changes
- **Overall Status**: Comprehensive status combining sale state, payment, and delivery (Draft, Confirmed - Pending Payment, Paid - Pending Delivery, Paid - Partial Delivery, In Progress, Completed, Overdue, Cancelled)
- **Payment Status**: Track payment progress (Pending, Partial, Paid, Overdue)
- **Delivery Status**: Monitor delivery progress (Not Shipped, Partially Shipped, Shipped, Delivered)
- **Order Progress**: Visual progress bar showing order completion percentage
- **Line Status**: Track individual order line items status

### 3. Advanced Grouping Capabilities
Group sales orders by:
- Vape Status
- Overall Status
- Report Category
- Priority Level
- Sales Region
- Customer Segment
- Payment Status
- Delivery Status

### 4. Analytics & Insights
- Days to Confirm: Track order confirmation time
- Order Age: Monitor how long orders have been open
- Fulfillment Progress: Track item-level delivery progress
- Sales Report Analysis: Pivot and graph views for data analysis

### 5. New Views & Dashboards
- **Sales Report Analysis**: Pivot and graph views with advanced analytics
- **Sales Status Dashboard**: Kanban view with comprehensive status overview

## Installation
1. Copy the module to your Odoo addons directory
2. Update the apps list (Settings → Apps → Update Apps List)
3. Search for "Sales Report Filter Grouping & Status"
4. Click Install

## Usage

### Setting Up Sales Orders
1. Open Sales → Orders → Quotations/Orders
2. In the "Other Information" tab, you'll find the new "Reporting & Status Information" section
3. Fill in the relevant fields:
   - Report Category
   - Priority Level
   - Sales Region
   - Delivery Status

### Using Advanced Filters
1. Open Sales → Orders → Quotations/Orders
2. Click on the search icon
3. Use the new filter options:
   - **Vape Status Filters** (Workflow stages):
     - Quotation
     - Sales Order
     - Send to Courier
     - Done (Delivered)
   - **Overall Status Filters**:
     - Completed Orders
     - In Progress
     - Pending Payment
     - Pending Delivery
     - Overdue
   - **Other Filters**:
     - High Priority
     - Urgent Priority
     - Payment Pending
     - Payment Overdue
     - Not Shipped
     - Delivered

### Grouping Sales Data
1. Open Sales → Orders → Quotations/Orders
2. Click on the search icon → Group By
3. Select grouping options:
   - Vape Status
   - Overall Status
   - Report Category
   - Priority Level
   - Sales Region
   - Customer Segment
   - Payment Status
   - Delivery Status

### Accessing Reports
1. **Sales Report Analysis**: Sales → Sales Report Analysis
   - Provides pivot tables and charts for detailed analysis
   - Group by region, category, and time periods

2. **Sales Status Dashboard**: Sales → Sales Status Dashboard
   - Kanban view with order status cards
   - Quick overview of payment and delivery status
   - Visual progress indicators

## Technical Details

### Dependencies
- base
- sale
- sale_management

### Models Extended
- `sale.order`: Added fields for filtering, grouping, and status tracking
- `sale.order.line`: Added line-level status tracking

### New Fields Added

#### Sale Order
- `vape_status`: Workflow status tracking (Quotation → Sales Order → Send to Courier → Done)
- `overall_status`: Comprehensive status combining sale, payment, and delivery
- `report_category`: Selection field for categorization
- `priority_level`: Priority management
- `sales_region`: Geographic region tracking
- `customer_segment`: Computed customer segmentation
- `payment_status`: Computed payment tracking
- `delivery_status`: Delivery progress tracking
- `order_progress`: Overall completion percentage
- `days_to_confirm`: Time to confirmation metric
- `order_age`: Days since order creation

#### Sale Order Line
- `line_status`: Individual line item status
- `fulfillment_progress`: Line-level fulfillment tracking

## POS Dashboard

### Overview
The POS Dashboard provides a comprehensive view of your Point of Sale performance with real-time statistics and KPIs.

### Features

#### Key Performance Indicators (KPIs)
- **Total Orders**: Total number of POS orders in the selected period
- **Total Revenue**: Sum of all completed POS orders
- **Average Order Value**: Average revenue per order
- **Total Margin**: Total profit margin from POS orders
- **Profit Margin %**: Percentage profit margin

#### Payment Tracking
- **Paid Orders**: Number of fully paid orders (clickable to view details)
- **Pending Orders**: Orders awaiting payment (clickable to view details)
- **Partial Payment**: Orders with partial payments

#### Customer Analytics
- **Total Customers**: Unique customers served
- **New Customers**: First-time customers
- **VIP Customers**: High-value repeat customers
- **Regular Customers**: Returning customers

#### Category Breakdown
- **Retail Orders**: Orders categorized as retail
- **Wholesale Orders**: Bulk/wholesale orders
- **Online Orders**: Online channel orders
- **Direct Sales**: Direct sales orders

#### Session Management
- **Active Sessions**: Currently open POS sessions
- **Closed Sessions**: Completed POS sessions

#### Regional Analysis
- **Central Sales**: Sales from central region
- **International Sales**: International sales revenue

### Accessing the POS Dashboard

1. Navigate to **Point of Sale → Dashboard**
2. Select the date range using Date From and Date To fields
3. View the comprehensive statistics displayed in organized sections
4. Click on clickable metrics (Orders, Paid Orders, Pending Orders) to drill down into details

### Dashboard Views

The POS Dashboard supports two view modes:

1. **Kanban View**: Visual tiles showing key metrics in an easy-to-read format
2. **Form View**: Detailed view with all statistics organized in groups

### Using Dashboard Actions

- Click on **Total Orders** to view all orders in the selected period
- Click on **Paid Orders** to see all fully paid orders
- Click on **Pending Orders** to review orders awaiting payment

## Courier Integration

### How it Works with delivery_courier_custom Module

The Vape Status field automatically integrates with the `delivery_courier_custom` module:

**Workflow:**
1. **Quotation**: Order is in draft/sent state
2. **Sales Order**: Order is confirmed, delivery order created
3. **Send to Courier**: When you click "Send Courier" button in delivery order
   - Delivery state changes to `courier_assigned`
   - Vape Status automatically updates to "Send to Courier"
   - Customer receives email notification
4. **Done (Delivered)**: When delivery is marked as delivered or validated
   - Delivery state changes to `done`
   - Vape Status automatically updates to "Done (Delivered)"

**Benefits:**
- Real-time status updates across sales and delivery
- No manual status updates needed
- Complete visibility of order lifecycle
- Integrated email notifications

**Without delivery_courier_custom:**
The module still works normally, tracking delivery based on standard Odoo picking states.

## Version
18.0.1.0.0

## License
LGPL-3

## Author
Your Company

## Support
For support and questions, please contact your system administrator.
