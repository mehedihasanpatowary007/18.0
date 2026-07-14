/** @odoo-module **/

const DEFAULT_SETTINGS = {
    user_id: false,
    user_name: "",
    timezone: "UTC",
    show_customizer_icon: true,
    icon_size: 70,
    text_size: 100,
    corner_radius: 96,
    app_gap: 16,
    fit_width: false,
    glassmorphism: false,
    animations: true,
    show_greeting_clock: true,
    show_search: true,
    background_opacity: 34,
    background_image: false,
    background_image_data_url: "",
    background_image_url: "",
};

let dashboardSettings = { ...DEFAULT_SETTINGS };
let dashboardRoot = null;
let clockTimer = null;
let observer = null;
let iconOverrideMap = {};

async function callUserMethod(method, args = []) {
    const response = await fetch(`/web/dataset/call_kw/res.users/${method}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: {
                model: "res.users",
                method,
                args,
                kwargs: {},
            },
        }),
    });
    const payload = await response.json();
    if (payload.error) {
        throw new Error(payload.error.data?.message || payload.error.message || "Dashboard RPC failed");
    }
    return payload.result;
}

function clampNumber(value, min, max, fallback) {
    const parsed = Number.parseInt(value, 10);
    if (Number.isNaN(parsed)) {
        return fallback;
    }
    return Math.min(Math.max(parsed, min), max);
}

function getGreetingHour() {
    const hour = new Date().getHours();
    if (hour < 5) {
        return ["&#9790;", "Good Night"];
    }
    if (hour < 12) {
        return ["&#9728;", "Good Morning"];
    }
    if (hour < 18) {
        return ["&#9728;", "Good Afternoon"];
    }
    return ["&#9790;", "Good Evening"];
}

function formatTime() {
    return new Intl.DateTimeFormat(undefined, {
        hour: "numeric",
        minute: "2-digit",
    }).format(new Date());
}

function findDashboardRoot() {
    return document.querySelector(".o_home_menu, .o_application_switcher, .o_apps");
}

function getAppItems(root) {
    if (!root) {
        return [];
    }
    const selector = ".o_app, .o_menuitem, a[role='menuitem'], button[role='menuitem']";
    return [...root.querySelectorAll(selector)].filter((item) => {
        return !item.closest(".zencore_dashboard_header, .zencore_dashboard_modal, .zencore_dashboard_customizer");
    });
}

function escapeHtml(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getAppLabel(item) {
    return item.textContent.trim().replace(/\s+/g, " ");
}

function getAppKey(item) {
    const href = item.getAttribute("href") || "";
    const match = href.match(/menu_id=([^&]+)/);
    return item.dataset.menuId || item.dataset.menuXmlid || (match && match[1]) || getAppLabel(item).toLowerCase();
}

function findAppIconNode(item) {
    return item.querySelector(".o_app_icon, img, .o_app_icon i, i");
}

function setIconOverrideMap(overrides) {
    iconOverrideMap = {};
    for (const override of overrides || []) {
        iconOverrideMap[override.app_key] = override;
    }
}

function applyIconOverrides(root) {
    if (!root) {
        return;
    }
    for (const item of getAppItems(root)) {
        const key = getAppKey(item);
        const override = iconOverrideMap[key];
        const iconNode = findAppIconNode(item);
        if (!iconNode) {
            continue;
        }
        if (iconNode.tagName === "IMG" && !iconNode.dataset.zencoreOriginalSrc) {
            iconNode.dataset.zencoreOriginalSrc = iconNode.src || "";
        } else if (!iconNode.dataset.zencoreOriginalBackground) {
            iconNode.dataset.zencoreOriginalBackground = iconNode.style.backgroundImage || "";
        }
        if (!override) {
            if (iconNode.tagName === "IMG" && iconNode.dataset.zencoreOriginalSrc) {
                iconNode.src = iconNode.dataset.zencoreOriginalSrc;
            } else {
                iconNode.style.backgroundImage = iconNode.dataset.zencoreOriginalBackground || "";
                iconNode.classList.remove("zencore_custom_app_icon");
            }
            continue;
        }
        if (iconNode.tagName === "IMG") {
            iconNode.src = override.icon_data_url || override.icon_url;
        } else {
            iconNode.style.backgroundImage = `url("${override.icon_data_url || override.icon_url}")`;
            iconNode.classList.add("zencore_custom_app_icon");
            iconNode.innerHTML = "";
        }
    }
}

function updateClock() {
    const header = document.querySelector(".zencore_dashboard_header");
    if (!header) {
        return;
    }
    const [icon, greeting] = getGreetingHour();
    const timeNode = header.querySelector(".zencore_dashboard_time");
    const greetingNode = header.querySelector(".zencore_dashboard_greeting");
    if (timeNode) {
        timeNode.textContent = formatTime();
    }
    if (greetingNode) {
        greetingNode.innerHTML = `<span>${icon}</span> ${greeting}, <strong>${dashboardSettings.user_name || ""}</strong>`;
    }
}

function applySearchFilter(root, term) {
    const normalizedTerm = term.trim().toLowerCase();
    for (const item of getAppItems(root)) {
        const label = item.textContent.trim().toLowerCase();
        item.classList.toggle("zencore_dashboard_hidden", Boolean(normalizedTerm && !label.includes(normalizedTerm)));
    }
}


function setRootStyles(root) {
    if (!root) {
        return;
    }
    const imageUrl = dashboardSettings.background_image_preview_url || (
        dashboardSettings.background_image ? (dashboardSettings.background_image_data_url || dashboardSettings.background_image_url) : ""
    );
    root.classList.add("zencore_dashboard_root");
    root.classList.toggle("zencore_dashboard_fit_width", dashboardSettings.fit_width);
    root.classList.toggle("zencore_dashboard_glass", dashboardSettings.glassmorphism);
    root.classList.toggle("zencore_dashboard_no_animation", !dashboardSettings.animations);
    const appGap = clampNumber(dashboardSettings.app_gap, 0, 40, 16);
    root.style.setProperty("--zencore-dashboard-icon-size", `${clampNumber(dashboardSettings.icon_size, 60, 128, 70)}px`);
    root.style.setProperty("--zencore-dashboard-text-size", `${clampNumber(dashboardSettings.text_size, 50, 250, 100)}%`);
    root.style.setProperty("--zencore-dashboard-radius", `${clampNumber(dashboardSettings.corner_radius, 0, 100, 96)}%`);
    root.style.setProperty("--zencore-dashboard-card-gap", `${appGap}px`);
    root.style.setProperty("--zencore-dashboard-card-half-gap", `${appGap / 2}px`);
    root.style.setProperty("--zencore-dashboard-bg-opacity", `${clampNumber(dashboardSettings.background_opacity, 0, 100, 34) / 100}`);
    root.style.setProperty("--zencore-dashboard-bg-image", imageUrl ? `url("${imageUrl}")` : "none");
}

function ensureHeader(root) {
    let header = root.querySelector(":scope > .zencore_dashboard_header");
    if (!header) {
        header = document.createElement("section");
        header.className = "zencore_dashboard_header";
        header.innerHTML = `
            <div class="zencore_dashboard_time"></div>
            <div class="zencore_dashboard_greeting"></div>
            <input class="zencore_dashboard_search" type="search" placeholder="Search apps..." />
        `;
        root.prepend(header);
        header.querySelector(".zencore_dashboard_search").addEventListener("input", (ev) => {
            applySearchFilter(root, ev.currentTarget.value);
        });
        header.querySelector(".zencore_dashboard_search").addEventListener("keydown", (ev) => {
            if (ev.key === "Escape") {
                ev.currentTarget.value = "";
                applySearchFilter(root, "");
            }
        });
    }
    header.classList.toggle("zencore_dashboard_header_hidden", !dashboardSettings.show_greeting_clock && !dashboardSettings.show_search);
    header.querySelector(".zencore_dashboard_time").hidden = !dashboardSettings.show_greeting_clock;
    header.querySelector(".zencore_dashboard_greeting").hidden = !dashboardSettings.show_greeting_clock;
    header.querySelector(".zencore_dashboard_search").hidden = !dashboardSettings.show_search;
    updateClock();
    if (!clockTimer) {
        clockTimer = window.setInterval(updateClock, 30000);
    }
}

function ensureCustomizerButton() {
    const systray = document.querySelector(".o_menu_systray");
    if (!systray) {
        return;
    }
    let button = systray.querySelector(".zencore_dashboard_customizer");
    if (!button) {
        button = document.createElement("button");
        button.type = "button";
        button.className = "zencore_dashboard_customizer";
        button.title = "Appearance Settings";
        button.setAttribute("aria-label", "Appearance Settings");
        button.innerHTML = `<i class="fa fa-th" aria-hidden="true"></i>`;
        button.addEventListener("click", () => openSettingsModal());
        systray.prepend(button);
    }
    button.hidden = !dashboardSettings.show_customizer_icon;
}

function getControlValue(modal, name, type = "number") {
    const control = modal.querySelector(`[name="${name}"]`);
    if (!control) {
        return type === "checkbox" ? false : "";
    }
    return type === "checkbox" ? control.checked : control.value;
}

function syncModalLabels(modal) {
    for (const range of modal.querySelectorAll("input[type='range']")) {
        const target = modal.querySelector(`[data-value-for="${range.name}"]`);
        if (target) {
            const suffix = target.dataset.suffix || "";
            target.textContent = `${range.value}${suffix}`;
        }
    }
}

function renderSettingsModal() {
    let backdrop = document.querySelector(".zencore_dashboard_modal_backdrop");
    if (backdrop) {
        return backdrop;
    }
    backdrop = document.createElement("div");
    backdrop.className = "zencore_dashboard_modal_backdrop";
    backdrop.hidden = true;
    backdrop.innerHTML = `
        <div class="zencore_dashboard_modal" role="dialog" aria-modal="true" aria-label="Appearance Settings">
            <header class="zencore_dashboard_modal_header">
                <div>
                    <span class="zencore_dashboard_modal_eyebrow">Workspace appearance</span>
                    <h3>Dashboard Studio</h3>
                </div>
                <button type="button" class="zencore_dashboard_close" aria-label="Close">
                    <i class="fa fa-times" aria-hidden="true"></i>
                </button>
            </header>
            <div class="zencore_dashboard_modal_body">
                <section class="zencore_setting_card">
                    <div class="zencore_setting_card_title">
                        <i class="fa fa-th-large" aria-hidden="true"></i>
                        <span>App tiles</span>
                    </div>
                    <div class="zencore_setting_control">
                        <label>Icon size <strong data-value-for="icon_size" data-suffix="px"></strong></label>
                        <input name="icon_size" type="range" min="60" max="128" />
                        <div class="zencore_dashboard_range_scale"><span>60px</span><span>128px</span></div>
                    </div>
                    <div class="zencore_setting_control">
                        <label>Text size <strong data-value-for="text_size" data-suffix="%"></strong></label>
                        <input name="text_size" type="range" min="50" max="250" />
                        <div class="zencore_dashboard_range_scale"><span>50%</span><span>250%</span></div>
                    </div>
                    <div class="zencore_setting_control">
                        <label>Corner radius <strong data-value-for="corner_radius" data-suffix="%"></strong></label>
                        <input name="corner_radius" type="range" min="0" max="100" />
                        <div class="zencore_dashboard_range_scale"><span>0%</span><span>100%</span></div>
                    </div>
                    <div class="zencore_setting_control">
                        <label>App spacing <strong data-value-for="app_gap" data-suffix="px"></strong></label>
                        <input name="app_gap" type="range" min="0" max="40" />
                        <div class="zencore_dashboard_range_scale"><span>0px</span><span>40px</span></div>
                    </div>
                </section>

                <section class="zencore_setting_card">
                    <div class="zencore_setting_card_title">
                        <i class="fa fa-magic" aria-hidden="true"></i>
                        <span>Custom app icons</span>
                    </div>
                    <div class="zencore_icon_editor">
                        <select name="custom_icon_app"></select>
                        <div class="zencore_upload_row">
                            <label class="zencore_upload_button">
                                <i class="fa fa-image" aria-hidden="true"></i>
                                <span>Upload icon</span>
                                <input name="custom_icon_file" type="file" accept="image/*" />
                            </label>
                            <button type="button" class="zencore_reset_icon" title="Reset selected app icon">
                                <i class="fa fa-undo" aria-hidden="true"></i>
                            </button>
                        </div>
                        <div class="zencore_icon_editor_hint">Select an app, upload your logo, and it will replace that app icon for your user.</div>
                    </div>
                </section>

                <section class="zencore_setting_card">
                    <div class="zencore_setting_card_title">
                        <i class="fa fa-sliders" aria-hidden="true"></i>
                        <span>Layout behavior</span>
                    </div>
                    <div class="zencore_setting_grid">
                        <label class="zencore_dashboard_checkbox"><input name="fit_width" type="checkbox" /><span>Fit to screen width</span></label>
                        <label class="zencore_dashboard_checkbox"><input name="glassmorphism" type="checkbox" /><span>Glass surface</span></label>
                        <label class="zencore_dashboard_checkbox"><input name="animations" type="checkbox" /><span>Motion effects</span></label>
                        <label class="zencore_dashboard_checkbox"><input name="show_greeting_clock" type="checkbox" /><span>Greeting & clock</span></label>
                        <label class="zencore_dashboard_checkbox"><input name="show_search" type="checkbox" /><span>Search bar</span></label>
                    </div>
                </section>

                <section class="zencore_setting_card">
                    <div class="zencore_setting_card_title">
                        <i class="fa fa-picture-o" aria-hidden="true"></i>
                        <span>Background</span>
                    </div>
                    <div class="zencore_setting_control">
                        <label>Image opacity <strong data-value-for="background_opacity" data-suffix="%"></strong></label>
                        <input name="background_opacity" type="range" min="0" max="100" />
                        <div class="zencore_dashboard_range_scale"><span>0%</span><span>100%</span></div>
                    </div>
                    <div class="zencore_upload_row">
                        <label class="zencore_upload_button">
                            <i class="fa fa-cloud-upload" aria-hidden="true"></i>
                            <span>Choose image</span>
                            <input name="background_image_file" type="file" accept="image/*" />
                        </label>
                        <button type="button" class="zencore_dashboard_clear_image" title="Remove background image">
                            <i class="fa fa-trash" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div class="zencore_dashboard_preview"></div>
                </section>
            </div>
            <footer class="zencore_dashboard_modal_footer">
                <button type="button" class="zencore_dashboard_reset">Reset all</button>
                <div class="zencore_footer_actions">
                    <button type="button" class="zencore_dashboard_cancel">Cancel</button>
                    <button type="button" class="zencore_dashboard_save">Apply changes</button>
                </div>
            </footer>
        </div>
    `;
    document.body.appendChild(backdrop);
    backdrop.querySelector(".zencore_dashboard_close").addEventListener("click", closeSettingsModal);
    backdrop.querySelector(".zencore_dashboard_cancel").addEventListener("click", closeSettingsModal);
    backdrop.addEventListener("click", (ev) => {
        if (ev.target === backdrop) {
            closeSettingsModal();
        }
    });
    backdrop.querySelectorAll("input[type='range']").forEach((input) => {
        input.addEventListener("input", () => syncModalLabels(backdrop));
    });
    backdrop.querySelector(".zencore_dashboard_clear_image").addEventListener("click", () => {
        backdrop.dataset.backgroundImage = "";
        delete backdrop.dataset.backgroundImagePreviewUrl;
        backdrop.querySelector("[name='background_image_file']").value = "";
        backdrop.querySelector(".zencore_dashboard_preview").style.backgroundImage = "";
    });
    backdrop.querySelector("[name='background_image_file']").addEventListener("change", (ev) => {
        const input = ev.currentTarget;
        const file = input?.files?.[0];
        if (!file) {
            return;
        }
        const reader = new FileReader();
        reader.addEventListener("load", () => {
            const result = String(reader.result || "");
            const base64 = result.includes(",") ? result.split(",")[1] : result;
            backdrop.dataset.backgroundImage = base64;
            backdrop.dataset.backgroundImagePreviewUrl = result;
            backdrop.querySelector(".zencore_dashboard_preview").style.backgroundImage = `url("${result}")`;
        });
        reader.readAsDataURL(file);
    });
    backdrop.querySelector("[name='custom_icon_file']").addEventListener("change", (ev) => {
        const input = ev.currentTarget;
        const file = input?.files?.[0];
        const select = backdrop.querySelector("[name='custom_icon_app']");
        const selected = select?.selectedOptions?.[0];
        if (!file || !selected?.value) {
            return;
        }
        const reader = new FileReader();
        reader.addEventListener("load", async () => {
            const result = String(reader.result || "");
            const base64 = result.includes(",") ? result.split(",")[1] : result;
            await saveIconOverride({
                app_key: selected.value,
                app_name: selected.dataset.appName || selected.textContent,
                icon: base64,
            });
            if (input) {
                input.value = "";
            }
        });
        reader.readAsDataURL(file);
    });
    backdrop.querySelector(".zencore_reset_icon").addEventListener("click", async () => {
        const select = backdrop.querySelector("[name='custom_icon_app']");
        if (select?.value) {
            await resetIconOverride(select.value);
        }
    });
    backdrop.querySelector(".zencore_dashboard_save").addEventListener("click", () => saveModalSettings(backdrop));
    backdrop.querySelector(".zencore_dashboard_reset").addEventListener("click", () => saveSettings({ ...DEFAULT_SETTINGS, user_name: dashboardSettings.user_name }));
    return backdrop;
}

function fillSettingsModal(backdrop) {
    backdrop.querySelector("[name='icon_size']").value = dashboardSettings.icon_size;
    backdrop.querySelector("[name='text_size']").value = dashboardSettings.text_size;
    backdrop.querySelector("[name='corner_radius']").value = dashboardSettings.corner_radius;
    backdrop.querySelector("[name='app_gap']").value = dashboardSettings.app_gap;
    backdrop.querySelector("[name='fit_width']").checked = dashboardSettings.fit_width;
    backdrop.querySelector("[name='glassmorphism']").checked = dashboardSettings.glassmorphism;
    backdrop.querySelector("[name='animations']").checked = dashboardSettings.animations;
    backdrop.querySelector("[name='show_greeting_clock']").checked = dashboardSettings.show_greeting_clock;
    backdrop.querySelector("[name='show_search']").checked = dashboardSettings.show_search;
    backdrop.querySelector("[name='background_opacity']").value = dashboardSettings.background_opacity;
    delete backdrop.dataset.backgroundImage;
    delete backdrop.dataset.backgroundImagePreviewUrl;
    backdrop.querySelector(".zencore_dashboard_preview").style.backgroundImage = dashboardSettings.background_image
        ? `url("${dashboardSettings.background_image_data_url || dashboardSettings.background_image_url}")`
        : "";
    fillIconSelector(backdrop);
    syncModalLabels(backdrop);
}

function fillIconSelector(backdrop) {
    const select = backdrop.querySelector("[name='custom_icon_app']");
    if (!select) {
        return;
    }
    const apps = dashboardRoot ? getAppItems(dashboardRoot).map((item) => ({
        key: getAppKey(item),
        label: getAppLabel(item),
    })).filter((app) => app.key && app.label) : [];
    select.innerHTML = apps.map((app) => `
        <option value="${escapeHtml(app.key)}" data-app-name="${escapeHtml(app.label)}">${escapeHtml(app.label)}${iconOverrideMap[app.key] ? " (custom)" : ""}</option>
    `).join("");
}

function openSettingsModal() {
    const backdrop = renderSettingsModal();
    fillSettingsModal(backdrop);
    backdrop.hidden = false;
}

function closeSettingsModal() {
    const backdrop = document.querySelector(".zencore_dashboard_modal_backdrop");
    if (backdrop) {
        backdrop.hidden = true;
    }
}

async function saveModalSettings(modal) {
    const values = {
        icon_size: clampNumber(getControlValue(modal, "icon_size"), 60, 128, 70),
        text_size: clampNumber(getControlValue(modal, "text_size"), 50, 250, 100),
        corner_radius: clampNumber(getControlValue(modal, "corner_radius"), 0, 100, 96),
        app_gap: clampNumber(getControlValue(modal, "app_gap"), 0, 40, 16),
        fit_width: getControlValue(modal, "fit_width", "checkbox"),
        glassmorphism: getControlValue(modal, "glassmorphism", "checkbox"),
        animations: getControlValue(modal, "animations", "checkbox"),
        show_greeting_clock: getControlValue(modal, "show_greeting_clock", "checkbox"),
        show_search: getControlValue(modal, "show_search", "checkbox"),
        background_opacity: clampNumber(getControlValue(modal, "background_opacity"), 0, 100, 34),
    };
    if ("backgroundImage" in modal.dataset) {
        values.background_image = modal.dataset.backgroundImage;
        values.background_image_preview_url = modal.dataset.backgroundImagePreviewUrl || "";
    }
    await saveSettings(values);
}

async function saveSettings(values) {
    dashboardSettings = {
        ...dashboardSettings,
        ...values,
    };
    applyDashboard();
    closeSettingsModal();
    try {
        const responseSettings = await callUserMethod("zencore_save_dashboard_settings", [values]);
        dashboardSettings = {
            ...dashboardSettings,
            ...responseSettings,
        };
        applyDashboard();
    } catch (error) {
        console.warn("Zencore Apps Dashboard: could not save settings", error);
    }
}

async function saveIconOverride(values) {
    try {
        const overrides = await callUserMethod("zencore_save_dashboard_icon_override", [values]);
        setIconOverrideMap(overrides);
        applyIconOverrides(dashboardRoot);
        const backdrop = document.querySelector(".zencore_dashboard_modal_backdrop");
        if (backdrop) {
            fillIconSelector(backdrop);
        }
    } catch (error) {
        console.warn("Zencore Apps Dashboard: could not save app icon", error);
    }
}

async function resetIconOverride(appKey) {
    try {
        const overrides = await callUserMethod("zencore_reset_dashboard_icon_override", [appKey]);
        setIconOverrideMap(overrides);
        applyIconOverrides(dashboardRoot);
        const backdrop = document.querySelector(".zencore_dashboard_modal_backdrop");
        if (backdrop) {
            fillIconSelector(backdrop);
        }
    } catch (error) {
        console.warn("Zencore Apps Dashboard: could not reset app icon", error);
    }
}

function applyDashboard() {
    dashboardRoot = findDashboardRoot();
    if (!dashboardRoot) {
        ensureCustomizerButton();
        return;
    }
    setRootStyles(dashboardRoot);
    ensureHeader(dashboardRoot);
    applyIconOverrides(dashboardRoot);
    ensureCustomizerButton();
}

async function loadDashboardSettings() {
    try {
        dashboardSettings = {
            ...DEFAULT_SETTINGS,
            ...(await callUserMethod("zencore_get_dashboard_settings")),
        };
        setIconOverrideMap(dashboardSettings.icon_overrides);
    } catch (error) {
        console.warn("Zencore Apps Dashboard: using default settings", error);
    }
    applyDashboard();
}

function scheduleApply() {
    window.requestAnimationFrame(applyDashboard);
}

function startObserver() {
    if (observer) {
        return;
    }
    observer = new MutationObserver(scheduleApply);
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        loadDashboardSettings();
        startObserver();
    });
} else {
    loadDashboardSettings();
    startObserver();
}
