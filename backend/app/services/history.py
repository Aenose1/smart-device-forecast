from __future__ import annotations

from datetime import date
from collections import defaultdict


def daily_series(rows: list[tuple[date, float]]) -> list[tuple[date, float]]:
    """Average multiple sources observed on the same day; sorted by date."""
    acc: dict[date, list[float]] = defaultdict(list)
    for d, p in rows:
        acc[d].append(float(p))
    return [(d, sum(v) / len(v)) for d, v in sorted(acc.items())]


def compute_stats(rows: list[tuple[date, float]]) -> dict | None:
    """Summary statistics over historical (date, price) records. None when there is no history."""
    if not rows:
        return None
    s = daily_series(rows)
    prices = [p for _, p in s]
    lo = min(s, key=lambda x: x[1])
    hi = max(s, key=lambda x: x[1])
    first, last = s[0], s[-1]
    drop = rise = None
    for (d0, p0), (d1, p1) in zip(s, s[1:]):
        ch = p1 - p0
        pct = ch / p0 * 100
        if ch < 0 and (drop is None or ch < drop["amount"]):
            drop = {"amount": round(ch, 2), "pct": round(pct, 2), "from_date": d0.isoformat(), "to_date": d1.isoformat()}
        if ch > 0 and (rise is None or ch > rise["amount"]):
            rise = {"amount": round(ch, 2), "pct": round(pct, 2), "from_date": d0.isoformat(), "to_date": d1.isoformat()}
    return {
        "records": len(rows),
        "first_date": first[0].isoformat(),
        "last_date": last[0].isoformat(),
        "current_price": round(last[1], 2),
        "min_price": round(lo[1], 2), "min_date": lo[0].isoformat(),
        "max_price": round(hi[1], 2), "max_date": hi[0].isoformat(),
        "avg_price": round(sum(prices) / len(prices), 2),
        "abs_change": round(last[1] - first[1], 2),
        "pct_change": round((last[1] - first[1]) / first[1] * 100, 2) if first[1] else None,
        "highest_drop": drop,
        "highest_increase": rise,
    }
