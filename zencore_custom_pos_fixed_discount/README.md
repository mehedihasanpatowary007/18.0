# Zencore POS Fixed Line Discount

This Odoo 18.0 addon adds fixed amount discounts to Point of Sale order lines while keeping the native percentage discount flow.

## Features

- Adds `Fixed Disc` on `pos.order.line`.
- Shows a discount type selector when the cashier taps the POS `%` line-discount button.
- Supports:
  - percentage discount through Odoo's native line discount,
  - fixed amount discount through a POS number popup,
  - both discounts on the same line.
- Applies percentage first, then subtracts the fixed amount.
- Caps fixed discount so the line cannot become negative.
- Reduces the taxable base, order total, receipt total, and backend POS order totals.
- Displays fixed discount in the POS cart/receipt orderline details.
- Adds `Fixed Disc` near `Disc.%` in the POS order backend form and POS order line list.
- POS Sales Analysis `Total Discount` includes both percentage and fixed discounts.
- POS Sales Analysis also has a separate `Fixed Discount` measure.

## Installation

1. Copy `zencore_custom_pos_fixed_discount` into your Odoo custom addons path.
2. Restart Odoo.
3. Update the Apps list.
4. Install **Zencore POS Fixed Line Discount**.
5. Open a POS session and use the `%` button on a selected order line.

When updating an existing installation, upgrade this module so Odoo rebuilds the
`report.pos.order` SQL view used by POS Sales Analysis.

## Usage

1. Select an order line in POS.
2. Tap `%`.
3. Choose **Percentage Discount (%)** to use Odoo's native percentage flow.
4. Choose **Fixed Discount (Amount)** to enter a fixed currency amount.

Example:

- Quantity: `10`
- Unit price: `80`
- Fixed discount: `100`
- Final line total: `700`

## Notes

- The fixed discount is stored on `pos.order.line.fixed_discount_amount`.
- Offline sync uses Odoo's POS model serialization because the field is included in POS loaded fields.
- The module does not modify Odoo core files.
- No GitHub push is performed by this deliverable.
