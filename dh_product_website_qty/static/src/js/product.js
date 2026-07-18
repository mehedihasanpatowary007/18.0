/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Product } from "@sale/js/product/product";

patch(Product, {
    props: {
        ...Product.props,
        display_product_qty_limits: { type: Boolean, optional: true },
        minimum_product_quantity: { type: Number, optional: true },
        maximum_product_quantity: { type: Number, optional: true },
        product_quantity_multipler: { type: Number, optional: true },
    },
});

patch(Product.prototype, {
    async setup() {
        await super.setup?.(...arguments);
        if (this.props.display_product_qty_limits) {
            this.props.quantity = this.props.minimum_product_quantity;
        } 
        else {
            this.props.quantity = 1;
        }
    }
});

