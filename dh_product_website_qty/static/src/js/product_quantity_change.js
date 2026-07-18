/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';
import VariantMixin from "@website_sale/js/sale_variant_mixin";

WebsiteSale.include({
 	onClickAddCartJSON: function (ev) {
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.closest('.input-group').find("input");
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var multiplier = parseFloat($input.data("quantity-multipler") || 1);
        var previousQty = parseFloat($input.val() || 0, 10);
        var is_cart_empty = ($input.data('is-cart-empty'));
        if (multiplier != 0){

            var quantity = ($link.has(".fa-minus").length ? -multiplier : multiplier) + previousQty;
        }
        else{
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
        }
        var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
        if (is_cart_empty){
            if (newQty === min){
                $input.val(0).trigger('change');
            }

        }
        if (newQty !== previousQty) {
            $input.val(newQty).trigger('change');
        }
        return false;
    },   
});