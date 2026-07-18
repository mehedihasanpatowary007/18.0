/** @odoo-module **/

import { whenReady } from "@odoo/owl";

// Wait for DOM and Odoo to be ready
whenReady(() => {
    // If already verified, skip
    const verified = sessionStorage.getItem("age_verified");
    if (verified === "true") {
        return;
    }

    // Get config from window (injected by template)
    const config = window.ageVerificationConfig || {};

    const title       = config.title        || "AGE VERIFICATION";
    const message     = config.message      || "The products available on this website are age-restricted and intended only for adults of legal smoking age.";
    const messageSub  = config.message_sub  || "By entering this website, you affirm you are of legal smoking age in your jurisdiction.";
    const fallbackUrl = config.fallback_url || "https://www.google.com";

    // Colors (new simple system)
    const titleBg    = config.title_bg || "#4da3ff";
    const mainBg     = config.main_bg  || "#2b2b2b";
    const yesBg      = config.yes_bg   || "#27ae60";
    const noBg       = config.no_bg    || "#c0392b";
    const textColor  = config.text_color || "#ffffff";

    const logoBase64  = config.logo         || "";
    const logoUrl     = config.logo_url     || "";

    // Build logo HTML - prefer URL over base64
    let logoHTML = "";

    if (logoUrl && logoUrl.length > 5 && logoUrl !== "False" && logoUrl !== "false") {
        logoHTML = `
            <div class="age-popup-logo">
                <img src="${logoUrl}" alt="Logo"
                     onerror="console.error('Logo failed to load from URL'); this.parentElement.style.display='none';"
                     onload="console.log('Logo loaded successfully from URL');"/>
            </div>
        `;
    } else if (logoBase64 && logoBase64.length > 50) {
        const imgSrc = `data:image/png;base64,${logoBase64}`;
        logoHTML = `
            <div class="age-popup-logo">
                <img src="${imgSrc}" alt="Logo"
                     onerror="console.error('Logo failed to load from Base64'); this.parentElement.style.display='none';"
                     onload="console.log('Logo loaded successfully from Base64');"/>
            </div>
        `;
    }

    // Build popup HTML
    const popupHTML = `
        <div class="age-popup-overlay" id="agePopup">
            <div class="age-popup-box">
                <h2>${title}</h2>
                <div class="age-popup-content">
                    ${logoHTML}
                    <div class="age-popup-message">
                        <p class="message-main">${message}</p>
                        <p class="message-sub">${messageSub}</p>
                    </div>
                    <div class="age-popup-buttons">
                        <button id="ageNo" class="age-btn-no">NO, I DON'T AGREE</button>
                        <button id="ageYes" class="age-btn-yes">YES, I AM OF LEGAL AGE</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Insert popup into DOM
    document.body.insertAdjacentHTML('beforeend', popupHTML);

    // Get elements
    const popup = document.getElementById("agePopup");
    const yesBtn = document.getElementById("ageYes");
    const noBtn = document.getElementById("ageNo");

    // Apply CSS variables for new simplified system
    if (popup) {
        popup.style.setProperty("--popup-title-bg", titleBg);
        popup.style.setProperty("--popup-main-bg", mainBg);
        popup.style.setProperty("--popup-yes-bg", yesBg);
        popup.style.setProperty("--popup-no-bg", noBg);
        popup.style.setProperty("--popup-text", textColor);
    }

    // Button actions
    if (yesBtn) {
        yesBtn.addEventListener("click", () => {
            sessionStorage.setItem("age_verified", "true");
            if (popup) popup.remove();
        });
    }

    if (noBtn) {
        noBtn.addEventListener("click", () => {
            window.location.href = fallbackUrl;
        });
    }

    console.log("Age verification popup initialized with colors:", {
        titleBg, mainBg, yesBg, noBg, textColor
    });
});
