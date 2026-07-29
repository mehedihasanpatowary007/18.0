import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";
import { roundPrecision } from "@web/core/utils/numbers";
import { parseFloat as parseFloatField } from "@web/views/fields/parsers";
import { patch } from "@web/core/utils/patch";

const hasOwn = (object, key) => Object.prototype.hasOwnProperty.call(object, key);

Orderline.props.line.shape.fixedDiscountAmount = { type: String, optional: true };

patch(PosOrderline.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.fixed_discount_amount = vals.fixed_discount_amount || 0;
    },

    set_fixed_discount_amount(amount) {
        const parsedAmount =
            typeof amount === "number"
                ? amount
                : isNaN(parseFloatField(amount))
                ? 0
                : parseFloatField(amount);
        const cappedAmount = this.get_capped_fixed_discount_amount(parsedAmount || 0);
        this.fixed_discount_amount = roundPrecision(cappedAmount, this.currency.rounding);
        this.order_id.recomputeOrderData();
        this.setDirty();
        return this.fixed_discount_amount;
    },

    get_fixed_discount_amount() {
        return this.get_capped_fixed_discount_amount(this.fixed_discount_amount || 0);
    },

    get_fixed_discount_for_quantity(quantity = this.get_quantity()) {
        if (!this.get_quantity()) {
            return 0;
        }
        return this.get_fixed_discount_amount() * Math.abs(quantity / this.get_quantity());
    },

    get_capped_fixed_discount_amount(amount) {
        const parsedAmount = Math.max(amount || 0, 0);
        return Math.min(parsedAmount, this.get_fixed_discount_base_amount());
    },

    get_fixed_discount_base_amount(quantity = this.get_quantity()) {
        const discountFactor = 1 - this.get_discount() / 100;
        return Math.abs(this.get_unit_price() * quantity * discountFactor);
    },

    prepareBaseLineForTaxesComputationExtraValues(customValues = {}) {
        const values = super.prepareBaseLineForTaxesComputationExtraValues(customValues);
        if (
            customValues.ignore_fixed_discount ||
            (hasOwn(customValues, "discount") && customValues.discount === 0.0) ||
            (hasOwn(customValues, "price_unit") && customValues.price_unit !== this.get_unit_price())
        ) {
            return values;
        }

        const quantity = values.quantity || 0;
        const discount = values.discount || 0;
        const discountFactor = 1 - discount / 100;
        if (!quantity || !discountFactor) {
            return values;
        }

        const discountedTotal = values.price_unit * quantity * discountFactor;
        const fixedDiscount = Math.min(
            this.get_fixed_discount_for_quantity(quantity),
            Math.abs(discountedTotal)
        );
        if (!fixedDiscount) {
            return values;
        }

        const sign = discountedTotal < 0 ? -1 : 1;
        const adjustedTotal = discountedTotal - sign * fixedDiscount;
        values.price_unit = adjustedTotal / (quantity * discountFactor);
        return values;
    },

    set_discount(discount) {
        super.set_discount(discount);
        this.fixed_discount_amount = this.get_fixed_discount_amount();
        this.order_id.recomputeOrderData();
        this.setDirty();
    },

    set_quantity(quantity, keep_price) {
        const result = super.set_quantity(...arguments);
        if (result === true) {
            this.fixed_discount_amount = this.get_fixed_discount_amount();
            this.order_id.recomputeOrderData();
            this.setDirty();
        }
        return result;
    },

    set_unit_price(price) {
        super.set_unit_price(...arguments);
        this.fixed_discount_amount = this.get_fixed_discount_amount();
        this.order_id.recomputeOrderData();
        this.setDirty();
    },

    can_be_merged_with(orderline) {
        return !this.get_fixed_discount_amount() && super.can_be_merged_with(orderline);
    },

    getDisplayData() {
        const data = super.getDisplayData();
        const fixedDiscount = this.get_fixed_discount_amount();
        return {
            ...data,
            fixedDiscountAmount: fixedDiscount
                ? formatCurrency(fixedDiscount, this.currency)
                : "",
        };
    },
});
