from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import find_visitor
from ..models import Device, Prediction, PriceHistory, User
from ..services.forecast_service import serialize_prediction

router = APIRouter(tags=["dashboard"])


def price_change_rows(db: Session) -> list[dict]:
    """First-vs-latest price change per device (devices with >= 2 distinct dates)."""
    da = (select(PriceHistory.device_id.label("device_id"), PriceHistory.date.label("date"),
                 func.avg(PriceHistory.price).label("p")).group_by(PriceHistory.device_id, PriceHistory.date).subquery())
    bounds = (select(da.c.device_id, func.min(da.c.date).label("d0"), func.max(da.c.date).label("d1"),
                     func.count().label("n")).group_by(da.c.device_id).subquery())
    f, l = da.alias("f"), da.alias("l")
    stmt = (select(Device.id, Device.name, Device.brand, Device.category, Device.currency, f.c.p.label("first"), l.c.p.label("last"))
            .join(bounds, bounds.c.device_id == Device.id)
            .join(f, and_(f.c.device_id == Device.id, f.c.date == bounds.c.d0))
            .join(l, and_(l.c.device_id == Device.id, l.c.date == bounds.c.d1)).where(bounds.c.n >= 2))
    out = []
    for r in db.execute(stmt):
        out.append({"id": r.id, "name": r.name, "brand": r.brand, "category": r.category, "currency": r.currency,
                    "first_price": round(r.first, 2), "latest_price": round(r.last, 2),
                    "pct_change": round((r.last - r.first) / r.first * 100, 2)})
    return out


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User | None = Depends(find_visitor)):
    counts = dict(db.execute(select(Device.category, func.count()).group_by(Device.category)).all())
    changes = price_change_rows(db)
    ranked = sorted(changes, key=lambda x: x["pct_change"])
    month = func.strftime("%Y-%m", PriceHistory.date) if db.bind.dialect.name == "sqlite" else func.to_char(PriceHistory.date, "YYYY-MM")
    by_month = db.execute(select(month.label("m"), func.count()).group_by("m").order_by("m")).all()
    uid = user.id if user else -1  # a browser that has made no forecast yet has no history
    recent = db.execute(select(Prediction).where(Prediction.user_id == uid)
                        .order_by(Prediction.created_at.desc(), Prediction.id.desc()).limit(5)).scalars().all()
    return {
        "total_devices": sum(counts.values()), "laptops": counts.get("Laptop", 0), "smartphones": counts.get("Smartphone", 0),
        "history_records": db.execute(select(func.count()).select_from(PriceHistory)).scalar_one(),
        "my_predictions": db.execute(select(func.count()).select_from(Prediction).where(Prediction.user_id == uid)).scalar_one(),
        "average_price_change": round(sum(c["pct_change"] for c in changes) / len(changes), 2) if changes else None,
        "top_decreases": [c for c in ranked if c["pct_change"] < 0][:5],
        "top_increases": [c for c in reversed(ranked) if c["pct_change"] > 0][:5],
        "records_by_month": [{"month": m, "records": n} for m, n in by_month][-24:],
        "recent_predictions": [serialize_prediction(p, full=False) for p in recent],
    }
