import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PosOrderline.prototype, {

    set_quantity(quantity, keep_price) {
        const is_restrict_negative = this?.order_id?.config_id?.is_restrict_negative
        const qty_available = this?.product_id?.qty_available
        const is_storable = this?.product_id?.is_storable
        if (is_restrict_negative && is_storable && quantity && (qty_available <= 0 || quantity > qty_available)){
            return {
                    title: _t("Insufficient Stock"),
                    body: _t(
                        `Stock limit reached for ${this?.product_id?.name}. Available quantity: ${qty_available}.`
                    ),
                };
        }
        else {
            return super.set_quantity(quantity, keep_price);
        }
    },

});
