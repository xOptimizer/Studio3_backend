"""Flat-rate shipping + tax constants. No carrier integration — matches the product
spec's simple tier list (Standard/Express/Overnight/Free)."""

SHIPPING_RATES_CENTS = {
    "standard": 500,
    "express": 1500,
    "overnight": 3500,
    "free": 0,
}

# Placeholder — matches the Flutter mock's hardcoded 8.25%, now computed server-side.
FLAT_TAX_RATE = 0.0825
