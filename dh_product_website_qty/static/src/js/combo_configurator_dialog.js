/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { onWillStart } from '@odoo/owl';
import { ComboConfiguratorDialog } from '@sale/js/combo_configurator_dialog/combo_configurator_dialog';
import { rpc } from "@web/core/network/rpc";

patch(ComboConfiguratorDialog.prototype, {
    async setup() {
        super.setup(...arguments);
        this.getProductValuesUrl = '/sale/product/get_values';

        const {
                display_product_qty_limits,
                minimum_product_quantity,
                maximum_product_quantity,
                product_quantity_multipler,
            } = await this._loadProductData(this.props.product_tmpl_id);

        this.state.display_product_qty_limits = display_product_qty_limits;
        this.state.minimum_product_quantity = minimum_product_quantity;
        this.state.maximum_product_quantity = maximum_product_quantity;
        this.state.product_quantity_multipler = product_quantity_multipler;

        if (this.state.display_product_qty_limits) {
            this.state.quantity = this.state.minimum_product_quantity;
        } else {
            this.state.quantity = 1;
        }
    },
    async _loadProductData(onlyMainProduct) {
        return rpc(this.getProductValuesUrl, {
            product_template_id: this.props.product_tmpl_id,
        });
    }
});
