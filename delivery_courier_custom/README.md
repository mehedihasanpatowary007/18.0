# Delivery Courier Custom Module

## Overview
This module extends Odoo 18's delivery functionality with a comprehensive courier management system, including automated email notifications and chatter integration.

## Features

### 1. Courier Management
- Create and manage courier records with detailed information:
  - Name, phone, email, mobile
  - Vehicle number and license number
  - Track deliveries assigned to each courier

### 2. Enhanced Delivery Workflow
- **New Courier Status Field**: Track delivery progress through courier states
  - Draft → Ready → Courier Assigned → Delivered
- **Send Courier Button**: Assign delivery to courier with one click
- **Mark as Delivered Button**: Confirm delivery completion

### 3. Automated Email Notifications
- Professional email template sent to customers when courier is assigned
- Includes:
  - Delivery order details
  - Courier information (name, phone)
  - Delivery address
  - List of products being delivered
  - Special instructions/notes

### 4. Chatter Integration
- Detailed courier assignment messages posted automatically
- Delivery completion tracking
- Full audit trail of courier activities

### 5. Enhanced Views
- Additional "Courier Information" tab on delivery orders
- Courier status badge in list views
- Filters for courier states (Ready, With Courier, Delivered)
- Group by courier status and assigned courier

## Installation

1. Copy the module to your Odoo addons directory:
   ```
   F:\odoo18\server\odoo\custom_addons18\delivery_courier_custom\
   ```

2. Update the apps list:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Delivery Courier Custom"

3. Install the module:
   - Click "Install" button

## Usage

### Setting Up Couriers

1. Navigate to **Inventory → Couriers → Couriers**
2. Click **New** to create a courier record
3. Fill in courier details:
   - Name (required)
   - Phone/Mobile
   - Email
   - Vehicle Number
   - License Number
4. Click **Save**

### Using the Courier Workflow

1. **Create a Delivery Order**:
   - Navigate to Inventory → Operations → Delivery Orders
   - Create or open an existing delivery order
   - Process normally until "Ready" state

2. **Assign to Courier**:
   - Open the delivery order
   - Go to "Courier Information" tab
   - Select a courier from the dropdown (or enter courier name/phone manually)
   - Add any special instructions in "Courier Notes"
   - Click **Send Courier** button

3. **What Happens**:
   - Courier status changes to "Courier Assigned"
   - Email is sent to customer with delivery details
   - Message is posted in chatter with full details
   - Notification confirms successful assignment

4. **Mark as Delivered**:
   - When delivery is completed, click **Mark as Delivered**
   - Status changes to "Delivered"
   - Completion message posted in chatter
   - Picking is automatically validated (if not already done)

### Email Customization

To customize the courier assignment email:

1. Navigate to **Settings → Technical → Email → Templates**
2. Search for "Delivery Courier Assignment"
3. Edit the template as needed
4. The template uses QWeb syntax and has access to:
   - `object`: The delivery order record
   - `object.partner_id`: Customer information
   - `object.courier_id`: Assigned courier
   - `object.move_ids`: Product lines

## Technical Details

### Models

**delivery.courier**
- `name`: Courier name
- `phone`: Phone number
- `email`: Email address
- `mobile`: Mobile number
- `vehicle_number`: Vehicle registration
- `license_number`: Driver's license
- `delivery_ids`: One2many to stock.picking
- `delivery_count`: Computed field

**stock.picking (inherited)**
- `courier_state`: Selection field (draft, ready, courier, delivered)
- `courier_id`: Many2one to delivery.courier
- `courier_name`: Char field for manual entry
- `courier_phone`: Char field for manual entry
- `courier_sent_date`: Datetime (read-only)
- `courier_delivered_date`: Datetime (read-only)
- `courier_notes`: Text field
- `show_send_courier`: Computed field for button visibility
- `show_mark_delivered`: Computed field for button visibility

### Methods

**stock.picking**
- `action_send_courier()`: Assigns courier and sends notifications
- `action_mark_delivered()`: Marks delivery as completed
- `_post_courier_message()`: Posts detailed message in chatter
- `_send_courier_email()`: Sends email to customer
- `_get_formatted_address()`: Formats customer address

## Dependencies

- stock
- delivery
- mail

## Security

Access rights are configured for:
- **Stock User**: Read, Write, Create
- **Stock Manager**: Full access including Delete

## Support

For issues or questions, please contact your Odoo administrator.

## Version History

### Version 18.0.1.0.0
- Initial release
- Courier management system
- Enhanced delivery workflow
- Email notifications
- Chatter integration

## License

LGPL-3
