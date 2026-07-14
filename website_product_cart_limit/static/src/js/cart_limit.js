/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";

publicWidget.registry.WebsiteProductCartLimit = publicWidget.Widget.extend({
    selector: ".oe_website_sale",
    events: {
        "click .o_wcl_limit_reached": "_onClickLimitReached",
        "click .css_quantity a": "_onClickProductQuantityButton",
        "change input[name='add_qty']": "_onChangeProductQuantity",
    },

    start() {
        this._super(...arguments);
        this._refreshProductQuantityState();
    },

    // Show the product-page warning and Odoo's top warning box.
    _showWarning(message) {
        const alert = document.querySelector(".o_wcl_product_limit_alert");
        if (alert) {
            alert.classList.remove("d-none");
        }
        if (message) {
            wSaleUtils.showWarning(message);
        }
    },

    // Clear only the warning created by this module.
    _clearLimitWarning() {
        const alert = document.querySelector(".o_wcl_product_limit_alert");
        if (alert) {
            alert.classList.add("d-none");
        }

        const topWarning = document.querySelector(".oe_website_sale > #data_warning");
        if (topWarning?.textContent.includes("Maximum Limit Reached")) {
            topWarning.remove();
        }
    },

    _getProductLimit() {
        const alert = document.querySelector(".o_wcl_product_limit_alert[data-limit]");
        return alert ? parseInt(alert.dataset.limit || "0", 10) : 0;
    },

    _getProductWarning(limit) {
        return `Maximum Limit Reached: You can buy a total of ${limit} units only.`;
    },

    _refreshProductQuantityState() {
        const limit = this._getProductLimit();
        const quantityInput = document.querySelector("input[name='add_qty']");
        if (!limit || !quantityInput) {
            return;
        }
        const quantity = parseInt(quantityInput.value || "1", 10) || 1;
        const limitedQuantity = Math.min(quantity, limit);
        const plusButton = quantityInput.closest(".css_quantity")?.querySelector("a:last-child");
        if (plusButton) {
            plusButton.classList.toggle("o_wcl_limit_reached", limitedQuantity >= limit);
            plusButton.classList.toggle("disabled", limitedQuantity >= limit);
            plusButton.dataset.limitWarning = this._getProductWarning(limit);
        }
        quantityInput.value = limitedQuantity;

        if (limitedQuantity < limit) {
            this._clearLimitWarning();
        }
    },

    _onClickLimitReached(ev) {
        ev.preventDefault();
        ev.stopImmediatePropagation();
        const message = ev.currentTarget.dataset.limitWarning;
        this._showWarning(message);
    },

    _onClickProductQuantityButton(ev) {
        const limit = this._getProductLimit();
        if (!limit) {
            return;
        }
        const quantityInput = ev.currentTarget.closest(".css_quantity")?.querySelector("input[name='add_qty']");
        if (!quantityInput) {
            return;
        }
        const isPlus = ev.currentTarget === ev.currentTarget.closest(".css_quantity").querySelector("a:last-child");
        const quantity = parseInt(quantityInput.value || "1", 10) || 1;
        if (isPlus && quantity >= limit) {
            ev.preventDefault();
            ev.stopImmediatePropagation();
            this._showWarning(this._getProductWarning(limit));
            return;
        }
        setTimeout(() => this._refreshProductQuantityState());
    },

    _onChangeProductQuantity() {
        const limit = this._getProductLimit();
        const quantityInput = document.querySelector("input[name='add_qty']");
        if (limit && quantityInput && parseInt(quantityInput.value || "1", 10) > limit) {
            quantityInput.value = limit;
            this._showWarning(this._getProductWarning(limit));
        }
        this._refreshProductQuantityState();
    },
});
