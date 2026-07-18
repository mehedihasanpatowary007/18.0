/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebsiteSale } from "@website_sale/js/website_sale";

WebsiteSale.include({
    _handleAdd: function ($form) {
        var self = this;
        this.$form = $form;

        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];

        const productTemplateId =
            parseInt($form.find('input[type="hidden"][name="product_template_id"]').first().val());
        var productReady = this.selectOrCreateProduct(
            $form,
            parseInt($form.find(productSelector.join(', ')).first().val(), 10),
            productTemplateId,
        );

        return productReady.then(function (productId) {
            $form.find(productSelector.join(', ')).val(productId);
            self._updateRootProduct($form, productId, productTemplateId);
            self._set_product_min_qty($form)
            return self._onProductReady($form.closest('.o_wsale_product_page').length > 0);
        });
    },

    _set_product_min_qty($form) {
        this.display_product_qty_limits = $form.find('input.product_display_product_qty').val();
        if(this.display_product_qty_limits){

            this.min_qty = parseInt($form.find('input.product_min_qty').val());
        }
        else{
            this.min_qty = 1
        }
        return this.min_qty;
    },

     _submitForm: function () {
        const params = this.rootProduct;
        const product_min_qty = this.min_qty
        const $product = $('#product_detail');
        const productTrackingInfo = $product.data('product-tracking-info');
        if (productTrackingInfo) {
            productTrackingInfo.quantity = params.quantity;
            $product.trigger('add_to_cart_event', [productTrackingInfo]);
        }
        if(this.display_product_qty_limits){
         if(isNaN(product_min_qty)){
            params.add_qty = params.quantity;
            }
            else{

                params.add_qty = product_min_qty;
            }
           
        }
        else{
            params.add_qty = params.quantity;   
        }
        
        // params.add_qty = params.quantity;
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        delete params.quantity;
        return this.addToCart(params);
    },     
});
