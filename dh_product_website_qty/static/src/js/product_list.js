/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductList } from "@sale/js/product_list/product_list";

patch(ProductList, {
    props: {
        ...ProductList.props,

        display_product_qty_limits: { type: Boolean, optional: true },
        minimum_product_quantity: { type: Number, optional: true },
        maximum_product_quantity: { type: Number, optional: true },
        product_quantity_multipler: { type: Number, optional: true },
    },
});