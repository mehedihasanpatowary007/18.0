# API endpoints (ONLY for server-to-server POST)
sandBoxUrl = "https://sandbox.aamarpay.com/jsonpost.php"
productionUrl = "https://secure.aamarpay.com/jsonpost.php"

# Merchant credentials (LIVE)
storeID = "thevapecafe"
signature = "48429a678501cbd44324ae8051e727d8"

# Callback URLs (used by Odoo, NOT by API endpoint)
succesUrl = "https://example.com/payment/confirm"
failUrl = "https://example.com/payment/fail"
cancelUrl = "https://example.com/payment/cancel"

# Optional (not used for API calls)
sandboxReturnUrl = "https://sandbox.aamarpay.com"
productionReturnUrl = "https://secure.aamarpay.com"
