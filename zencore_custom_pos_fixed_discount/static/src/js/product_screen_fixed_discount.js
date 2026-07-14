import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    async onNumpadClick(buttonValue) {
        if (buttonValue !== "discount") {
            return super.onNumpadClick(...arguments);
        }

        const selectedLine = this.pos.get_order()?.get_selected_orderline();
        if (!selectedLine) {
            return super.onNumpadClick(...arguments);
        }

        const discountType = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select Discount Type"),
            list: [
                {
                    id: "percentage",
                    label: _t("Percentage Discount (%)"),
                    item: "percentage",
                    isSelected: true,
                },
                {
                    id: "fixed",
                    label: _t("Fixed Discount (Amount)"),
                    item: "fixed",
                },
            ],
        });

        if (discountType === "percentage") {
            return super.onNumpadClick(...arguments);
        }
        if (discountType !== "fixed") {
            return;
        }

        this.numberBuffer.capture();
        this.numberBuffer.reset();

        const inputAmount = await makeAwaitable(this.dialog, NumberPopup, {
            title: _t("Set Fixed Discount Amount"),
            startingValue: selectedLine.get_fixed_discount_amount() || "",
            placeholder: _t("Amount"),
        });
        if (inputAmount === undefined) {
            return;
        }

        const amount = Math.max(
            0,
            this.env.utils.parseValidFloat(inputAmount.toString()) || 0
        );
        const cappedAmount = selectedLine.get_capped_fixed_discount_amount(amount);
        selectedLine.set_fixed_discount_amount(cappedAmount);
        this.pos.numpadMode = "quantity";

        if (amount > cappedAmount) {
            this.dialog.add(AlertDialog, {
                title: _t("Fixed discount adjusted"),
                body: _t("The fixed discount cannot be higher than the current line subtotal."),
            });
        }
    },
});
