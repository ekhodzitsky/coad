# billing

## Purpose

Own discount total calculation for checkout presentation.

## Surfaces

- `BillingTotals`: includes `discount_cents`.

## Consumers

- Missing on purpose in `MODULE_CONTRACT.md`.

## Verification

```bash
python -m pytest tests/test_billing.py
```
