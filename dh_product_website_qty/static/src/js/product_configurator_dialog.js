/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { onWillStart } from '@odoo/owl';
import { ProductConfiguratorDialog } from '@sale/js/product_configurator_dialog/product_configurator_dialog';
import { rpc } from "@web/core/network/rpc";

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup(...arguments);
        this.getProductValuesUrl = '/sale/product/get_values';
        
        onWillStart(async () => {
            const {
                display_product_qty_limits,
                minimum_product_quantity,
                maximum_product_quantity,
                product_quantity_multipler,
            } = await this._loadProductData(this.env.mainProductTmplId);

            this.state.display_product_qty_limits = display_product_qty_limits;
            this.state.minimum_product_quantity = minimum_product_quantity;
            this.state.maximum_product_quantity = maximum_product_quantity;
            this.state.product_quantity_multipler = product_quantity_multipler;
        });
    },
    async _loadProductData(onlyMainProduct) {
        return rpc(this.getProductValuesUrl, {
            product_template_id: this.props.productTemplateId,
        });
    }
});
