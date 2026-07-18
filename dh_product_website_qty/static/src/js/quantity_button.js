/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { QuantityButtons } from "@sale/js/quantity_buttons/quantity_buttons";  // Adjust import path if needed

patch(QuantityButtons, {
    props: {
        ...QuantityButtons.props,
         display_product_qty_limits: { type: Boolean, optional: true },
        minimum_product_quantity: { type: Number, optional: true },
        maximum_product_quantity: { type: Number, optional: true },
        product_quantity_multipler: { type: Number, optional: true },
    },
});


patch(QuantityButtons.prototype, {
    increaseQuantity() {
        if (this.props.display_product_qty_limits) {
            const addedQuantity = this.props.quantity + this.props.product_quantity_multipler;
            if (addedQuantity <= this.props.maximum_product_quantity) {
                this.props.setQuantity(addedQuantity);
            } else {
                this.props.setQuantity(this.props.quantity + 1);
            }
        } else {
            this.props.setQuantity(this.props.quantity + 1);
        }
    },
    decreaseQuantity() {
        if (this.props.display_product_qty_limits){

            var decrease_quanity =  this.props.quantity -this.props.product_quantity_multipler
            if (this.props.minimum_product_quantity <= decrease_quanity){
                this.props.setQuantity(this.props.quantity - this.props.product_quantity_multipler);

            }
            else{
                this.props.setQuantity(this.props.quantity - 1);
            }
        }
        else{
            this.props.setQuantity(this.props.quantity - 1);   
        }
    }
});
