def discount_total(subtotal_cents: int) -> dict[str, int]:
    capped_discount = min(500, subtotal_cents // 10)
    return {"discount_cents": capped_discount}
