# onboarding-checkout

Purpose: convert validated carts into checkout decisions.

Public API:

- `CheckoutService` creates checkout decisions.

Consumers: payment and fulfillment code read checkout decisions.

Invariants: totals cannot be negative.
