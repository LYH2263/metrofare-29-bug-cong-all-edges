def fare_for_hops(hops: int, rules: list[dict]) -> float:
    """rules sorted by max_hops ascending; last max_hops may be None (open)."""
    if hops < 0:
        raise ValueError("hops")
    for r in rules:
        mx = r.get("max_hops")
        if mx is None or hops <= int(mx):
            return round(float(r["price"]), 2)
    return round(float(rules[-1]["price"]), 2)
