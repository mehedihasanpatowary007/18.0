/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";

const originalShowCartNotification = wSaleUtils.showCartNotification;

// Hide the success cart widget when the server rejected the add by cart limit.
wSaleUtils.showCartNotification = function (callService, props = {}, options = {}) {
    if (props.warning?.includes("Maximum Limit Reached")) {
        props = { ...props, lines: undefined };
    }
    return originalShowCartNotification(callService, props, options);
};

function removeCartLimitSuccessNotifications() {
    const wrapperSelector = [
        ".o_notification",
        ".toast",
        ".modal",
        ".popover",
        ".card",
        "[role='dialog']",
        "[role='alert']",
    ].join(", ");
    for (const element of document.querySelectorAll("body *")) {
        if (!element.textContent.includes("Item(s) added to your cart")) {
            continue;
        }
        element.closest(wrapperSelector)?.remove();
    }
}

publicWidget.registry.WebsiteProductCartLimit = publicWidget.Widget.extend({
    selector: ".oe_website_sale",
    events: {
        "click .o_wcl_limit_reached": "_onClickLimitReached",
        "click .css_quantity a": "_onClickProductQuantityButton",
        "change input[name='add_qty']": "_onChangeProductQuantity",
    },

    start() {
        this._boundCaptureLimitClick = this._onCaptureLimitClick.bind(this);
        this.el.addEventListener("click", this._boundCaptureLimitClick, true);
        this._super(...arguments);
        this._refreshProductQuantityState();
    },

    destroy() {
        this.el.removeEventListener("click", this._boundCaptureLimitClick, true);
        return this._super(...arguments);
    },

    // Show the product-page warning and Odoo's top warning box on blocked clicks.
    _showWarning(message) {
        this._toggleInlineWarning(true, message);
        if (message) {
            wSaleUtils.showWarning(message);
        }
    },

    // Show or hide the inline product-page limit message.
    _toggleInlineWarning(show, message = "") {
        const alert = document.querySelector(".o_wcl_product_limit_alert");
        if (alert) {
            alert.classList.toggle("d-none", !show);
            const messageNode = alert.querySelector(".o_wcl_product_limit_message");
            if (messageNode && message) {
                messageNode.textContent = message;
            }
        }
    },

    // Clear only the warning created by this module.
    _clearLimitWarning() {
        this._toggleInlineWarning(false);

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

    _setProductCartQty(quantity) {
        const alert = this._getProductLimitAlert();
        if (alert) {
            alert.dataset.cartQty = Math.max(quantity, 0).toString();
        }
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

    // Stop Odoo's own click handlers before they can add or show success.
    _onCaptureLimitClick(ev) {
        const blockedElement = ev.target.closest(".o_wcl_limit_reached");
        if (blockedElement && this.el.contains(blockedElement)) {
            ev.preventDefault();
            ev.stopImmediatePropagation();
            this._showWarning(blockedElement.dataset.limitWarning || this._getProductWarning(this._getProductLimit()));
            return;
        }

        const button = ev.target.closest("#add_to_cart, .o_we_buy_now, .a-submit");
        if (!button || !this.el.contains(button) || !this._getProductLimit()) {
            return;
        }

        if (this._shouldBlockProductAdd()) {
            ev.preventDefault();
            ev.stopImmediatePropagation();
            this._showWarning(button.dataset.limitWarning || this._getProductWarning(this._getProductLimit()));
            return;
        }

        const addQty = this._getProductAddQty();
        this._scheduleProductAddRecord(addQty);
    },

    _shouldBlockProductAdd() {
        const limit = this._getProductLimit();
        if (!limit) {
            return false;
        }
        const cartQty = this._getProductCartQty();
        const addQty = this._getProductAddQty();
        return cartQty >= limit || cartQty + addQty > limit;
    },

    _getProductAddQty() {
        const quantityInput = this._getProductQuantityInput();
        return parseInt(quantityInput?.value || "1", 10) || 1;
    },

    // Odoo updates cart widgets asynchronously, so refresh more than once.
    _scheduleProductAddRecord(addQty) {
        const limit = this._getProductLimit();
        const targetQty = Math.min(this._getProductCartQty() + addQty, limit);
        for (const delay of [0, 100, 350, 800]) {
            setTimeout(() => this._recordProductAdd(targetQty), delay);
        }
    },

    // Keep the page state updated after a valid add without requiring reload.
    _recordProductAdd(targetQty) {
        const limit = this._getProductLimit();
        if (!limit || !targetQty) {
            return;
        }
        this._setProductCartQty(targetQty);
        this._refreshProductQuantityState();
        if (this._getProductCartQty() >= limit) {
            this._removeAddToCartSuccessNotification();
        }
    },

    // Remove the success widget when the add has already reached the max limit.
    _removeAddToCartSuccessNotification() {
        removeCartLimitSuccessNotifications();
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
            plusButton.setAttribute("aria-disabled", plusBlocked ? "true" : "false");
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

        if (cartQty >= limit) {
            this._toggleInlineWarning(true, warning);
        } else if (cartQty + limitedQuantity < limit) {
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
