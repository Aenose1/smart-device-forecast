from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..errors import AppError
from ..models import Device, PriceHistory, User
from ..schemas import specs_to_dict
from ..services.history import compute_stats
from ..services.reports import history_csv

router = APIRouter(prefix="/devices", tags=["devices"])


def device_out(d: Device, latest: float | None = None, latest_date: date | None = None) -> dict:
    return {"id": d.id, "name": d.name, "brand": d.brand, "category": d.category,
            "release_date": d.release_date.isoformat() if d.release_date else None,
            "launch_price": d.launch_price, "current_price": d.current_price,
            "latest_price": latest if latest is not None else (d.current_price or d.launch_price),
            "latest_price_date": latest_date.isoformat() if latest_date else None,
            "currency": d.currency, "status": d.status, "specs": specs_to_dict(d)}


def _like(term: str) -> str:
    return "%" + term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def _latest_sq():
    return (select(PriceHistory.price).where(PriceHistory.device_id == Device.id)
            .order_by(PriceHistory.date.desc()).limit(1).scalar_subquery())


def _latest_date_sq():
    return select(func.max(PriceHistory.date)).where(PriceHistory.device_id == Device.id).scalar_subquery()


@router.get("/search")
@router.get("")
def search_devices(q: str | None = Query(None, max_length=100), category: str | None = Query(None, pattern="^(Laptop|Smartphone)$"),
                   brand: str | None = Query(None, max_length=80), min_price: float | None = Query(None, ge=0),
                   max_price: float | None = Query(None, ge=0), page: int = Query(1, ge=1),
                   page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise AppError(422, "invalid_range", "Minimum price cannot exceed maximum price.")
    latest = func.coalesce(_latest_sq(), Device.current_price, Device.launch_price)
    stmt = select(Device, latest.label("latest"), _latest_date_sq().label("latest_date"))
    if q and q.strip():
        t = _like(q.strip())
        stmt = stmt.where(or_(Device.name.ilike(t, escape="\\"), Device.brand.ilike(t, escape="\\"),
                              Device.category.ilike(t, escape="\\"), Device.id.ilike(t, escape="\\")))
    if category:
        stmt = stmt.where(Device.category == category)
    if brand:
        stmt = stmt.where(func.lower(Device.brand) == brand.lower())
    if min_price is not None:
        stmt = stmt.where(latest >= min_price)
    if max_price is not None:
        stmt = stmt.where(latest <= max_price)
    total = db.execute(select(func.count()).select_from(stmt.order_by(None).subquery())).scalar_one()
    rows = db.execute(stmt.order_by(Device.name).limit(page_size).offset((page - 1) * page_size)).all()
    return {"items": [device_out(d, lp, ld) for d, lp, ld in rows], "total": total, "page": page, "page_size": page_size}


@router.get("/brands")
def brands(category: str | None = Query(None, pattern="^(Laptop|Smartphone)$"), db: Session = Depends(get_db)):
    stmt = select(Device.brand).distinct().order_by(Device.brand)
    if category:
        stmt = stmt.where(Device.category == category)
    return db.execute(stmt).scalars().all()


def get_device_or_404(db: Session, device_id: str) -> Device:
    d = db.get(Device, device_id)
    if not d:
        raise AppError(404, "device_not_found", f"Device '{device_id}' was not found.")
    return d


@router.get("/{device_id}")
def get_device(device_id: str, db: Session = Depends(get_db)):
    d = get_device_or_404(db, device_id)
    rows = db.execute(select(PriceHistory.date, PriceHistory.price).where(PriceHistory.device_id == d.id)
                      .order_by(PriceHistory.date.desc()).limit(1)).first()
    return device_out(d, rows.price if rows else None, rows.date if rows else None)


@router.get("/{device_id}/history")
def device_history(device_id: str, format: str = Query("json", pattern="^(json|csv)$"), db: Session = Depends(get_db)):
    d = get_device_or_404(db, device_id)
    rows = db.execute(select(PriceHistory).where(PriceHistory.device_id == d.id).order_by(PriceHistory.date)).scalars().all()
    if format == "csv":
        return Response(history_csv(d, rows), media_type="text/csv",
                        headers={"Content-Disposition": f'attachment; filename="{d.id}_price_history.csv"'})
    return {"device_id": d.id, "currency": d.currency,
            "history": [{"date": r.date.isoformat(), "price": r.price, "source": r.source, "is_sample": r.is_sample} for r in rows],
            "stats": compute_stats([(r.date, r.price) for r in rows]),
            "has_sample_data": any(r.is_sample for r in rows)}
