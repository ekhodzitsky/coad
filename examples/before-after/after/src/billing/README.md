# billing

## Purpose

Own discount total calculation for checkout presentation.

## Surfaces

- `BillingTotals`: includes `discount_cents`.

## Consumers

- `src/checkout/checkout.py`

## Invariants

- Discount totals must never make checkout totals negative.

## Verification

```bash
python -m pytest tests/test_billing.py
```
