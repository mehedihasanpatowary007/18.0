# Website Product Cart Quantity Limit

Odoo 18 addon that limits how many units of a product a website customer can keep in the cart.

## Features

- Adds **Maximum Cart Quantity** in the product **Sales** tab.
- Shows the backend field only when the product is published on the website.
- Limits quantity on product add-to-cart and cart quantity updates.
- Disables the website/cart plus button once the limit is reached.
- Disables Add to Cart when the customer already has the maximum allowed quantity in cart.
- Shows a top warning popup when the customer clicks the disabled plus button.
- Clears the product-page warning automatically when quantity is decreased below the limit.
- Blocks checkout/payment if an existing cart is above the configured limit.
- A value of `0` means no limit.

## Installation

1. Copy `website_product_cart_limit` into your Odoo addons path.
2. Update the Apps list.
3. Install **Website Product Cart Quantity Limit**.
4. Open a product and set **Maximum Cart Quantity**.

## Notes

The limit is stored on `product.template`, so all variants of the same product template share the same maximum quantity.
