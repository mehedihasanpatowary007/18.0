/** @odoo-module **/



import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ProductConfiguratorPopup } from "@point_of_sale/app/store/product_configurator_popup/product_configurator_popup";





/* ----------------------------------------------------
   PATCH PRODUCT CONFIGURATOR POPUP
---------------------------------------------------- */
patch(ProductConfiguratorPopup.prototype, {
    confirm() {
        console.log("Custom Confirm Logic!");

        const product = this.state.product;   // correct product reference

        // Example stock check (as needed)
        if (product?.qty_available <= 0) {
            this.env.services.dialog.add(AlertDialog, {
                title: _t("Insufficient Stock"),
                body: _t(`Stock limit reached for ${product.name}. Available quantity: ${product.qty_available}.`),
            });
            return; // prevent confirm
        }

        // Call original behavior
        super.confirm();
    },
});



/* ----------------------------------------------------
   PATCH PRODUCT SCREEN
---------------------------------------------------- */
patch(ProductScreen.prototype, {

    async addProductToOrder(product, options) {

        const is_restrict_negative = this.pos?.config?.is_restrict_negative;
        const quantityByProductTmplId = this.state?.quantityByProductTmplId || {};
        const qtyAlreadyAdded = quantityByProductTmplId[product.product_tmpl_id?.id] || 0;

        const is_storable = product.is_storable;

        // Detect if product has variants
        const hasVariants =
            product.attribute_line_ids?.length &&
            product.attribute_line_ids[0]?.product_template_value_ids?.length;

        console.log("Product:", product);
        console.log("Has Variants:", hasVariants ? "YES" : "NO");
        console.log("qtyAlreadyAdded:", qtyAlreadyAdded);


        // CASE 1: Variant product → open popup directly
        if (hasVariants) {
            console.log("Variant product → letting POS open configurator popup.");
            await super.addProductToOrder(product, options);
            return;
        }

        // CASE 2: NO VARIANT → check stock restriction
        if (
            is_restrict_negative &&
            is_storable &&
            (product.qty_available <= 0 || qtyAlreadyAdded >= product.qty_available)
        ) {
            this.dialog.add(AlertDialog, {
                title: _t("Insufficient Stock"),
                body: _t(
                    `Stock limit reached for ${product.name}. Available quantity: ${product.qty_available}.`
                ),
            });
            return;
        }

        // DEFAULT BEHAVIOR
        await super.addProductToOrder(product, options);
    },
});

