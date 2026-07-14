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
        this._boundCaptureAddToCart = this._onCaptureAddToCart.bind(this);
        this.el.addEventListener("click", this._boundCaptureAddToCart, true);
        this._super(...arguments);
        this._refreshProductQuantityState();
    },

    destroy() {
        this.el.removeEventListener("click", this._boundCaptureAddToCart, true);
        return this._super(...arguments);
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

    _getProductLimitAlert() {
        return document.querySelector(".o_wcl_product_limit_alert[data-limit]");
    },

    _getProductLimit() {
        const alert = this._getProductLimitAlert();
        return alert ? parseInt(alert.dataset.limit || "0", 10) : 0;
    },

    _getProductCartQty() {
        const alert = this._getProductLimitAlert();
        return alert ? parseInt(alert.dataset.cartQty || "0", 10) : 0;
    },

    _getProductWarning(limit, cartQty = this._getProductCartQty()) {
        if (cartQty) {
            return `Maximum Limit Reached: You already have ${cartQty} in your cart. You can buy a total of ${limit} units only.`;
        }
        return `Maximum Limit Reached: You can buy a total of ${limit} units only.`;
    },

    _getProductQuantityInput() {
        return document.querySelector("input[name='add_qty']");
    },

    _getProductActionButtons() {
        return document.querySelectorAll("#add_to_cart, .o_we_buy_now, .a-submit");
    },

    // Stop Odoo's add-to-cart flow when the cart already reached the limit.
    _onCaptureAddToCart(ev) {
        const button = ev.target.closest("#add_to_cart, .o_we_buy_now, .a-submit");
        if (!button || !this.el.contains(button) || !this._shouldBlockProductAdd()) {
            return;
        }
        ev.preventDefault();
        ev.stopImmediatePropagation();
        this._showWarning(button.dataset.limitWarning || this._getProductWarning(this._getProductLimit()));
    },

    _shouldBlockProductAdd() {
        const limit = this._getProductLimit();
        if (!limit) {
            return false;
        }
        const cartQty = this._getProductCartQty();
        const quantityInput = this._getProductQuantityInput();
        const addQty = parseInt(quantityInput?.value || "1", 10) || 1;
        return cartQty >= limit || cartQty + addQty > limit;
    },

    _refreshProductQuantityState() {
        const limit = this._getProductLimit();
        const cartQty = this._getProductCartQty();
        const remainingQty = Math.max(limit - cartQty, 0);
        const quantityInput = this._getProductQuantityInput();
        if (!limit || !quantityInput) {
            return;
        }
        const quantity = parseInt(quantityInput.value || "1", 10) || 1;
        const limitedQuantity = remainingQty ? Math.min(quantity, remainingQty) : quantity;
        const warning = this._getProductWarning(limit, cartQty);
        const plusButton = quantityInput.closest(".css_quantity")?.querySelector("a:last-child");
        if (plusButton) {
            const plusBlocked = remainingQty <= 0 || limitedQuantity >= remainingQty;
            plusButton.classList.toggle("o_wcl_limit_reached", plusBlocked);
            plusButton.classList.toggle("disabled", plusBlocked);
            plusButton.dataset.limitWarning = warning;
        }
        quantityInput.value = limitedQuantity;

        for (const button of this._getProductActionButtons()) {
            const addBlocked = remainingQty <= 0 || cartQty + limitedQuantity > limit;
            button.classList.toggle("o_wcl_limit_reached", addBlocked);
            button.classList.toggle("disabled", addBlocked);
            button.setAttribute("aria-disabled", addBlocked ? "true" : "false");
            button.dataset.limitWarning = warning;
        }

        if (cartQty + limitedQuantity < limit) {
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
        const remainingQty = Math.max(limit - this._getProductCartQty(), 0);
        if (isPlus && (remainingQty <= 0 || quantity >= remainingQty)) {
            ev.preventDefault();
            ev.stopImmediatePropagation();
            this._showWarning(this._getProductWarning(limit));
            return;
        }
        setTimeout(() => this._refreshProductQuantityState());
    },

    _onChangeProductQuantity() {
        const limit = this._getProductLimit();
        const remainingQty = Math.max(limit - this._getProductCartQty(), 0);
        const quantityInput = this._getProductQuantityInput();
        if (limit && quantityInput && remainingQty && parseInt(quantityInput.value || "1", 10) > remainingQty) {
            quantityInput.value = remainingQty;
            this._showWarning(this._getProductWarning(limit));
        }
        this._refreshProductQuantityState();
    },
});
