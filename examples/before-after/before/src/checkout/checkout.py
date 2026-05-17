from src.billing.discounts import discount_total


def checkout_summary(subtotal_cents: int) -> dict[str, int]:
    totals = discount_total(subtotal_cents)
    return {
        "subtotal_cents": subtotal_cents,
        "discount_cents": totals["discount_cents"],
        "total_cents": subtotal_cents - totals["discount_cents"],
    }
