"""Public (no sign-in) catalogue overview used by the landing page: brand lists and a few featured devices.
Read-only; exposes only catalogue data (names, brands, specs, reference prices), never user data."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Device
from .devices import _latest_date_sq, _latest_sq, device_out

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    brand_rows = db.execute(select(Device.category, Device.brand, func.count()).group_by(Device.category, Device.brand)
                            .order_by(Device.category, Device.brand)).all()
    brands: dict[str, list[dict]] = {"Smartphone": [], "Laptop": []}
    for cat, brand, n in brand_rows:
        brands.setdefault(cat, []).append({"brand": brand, "devices": n})
    latest = func.coalesce(_latest_sq(), Device.current_price, Device.launch_price)
    rows = db.execute(select(Device, latest.label("latest"), _latest_date_sq().label("latest_date"))
                      .where(Device.status == "Active").order_by(Device.launch_price.desc())).all()
    # one device per brand (the highest-priced), alternating phones / laptops, so the showcase is varied
    seen: set[tuple[str, str]] = set()
    by_cat: dict[str, list] = {"Smartphone": [], "Laptop": []}
    for d, lp, ld in rows:
        key = (d.category, d.brand)
        if key in seen:
            continue
        seen.add(key)
        by_cat.setdefault(d.category, []).append(device_out(d, lp, ld))
    featured: list[dict] = []
    for i in range(8):
        for cat in ("Smartphone", "Laptop"):
            if i < len(by_cat.get(cat, [])) and len(featured) < 8 and i < 4:
                featured.append(by_cat[cat][i])
    total = sum(b["devices"] for lst in brands.values() for b in lst)
    return {"brands": brands, "featured": featured, "total_devices": total}
