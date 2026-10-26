"""Bootstrap helpers: admin account and the clearly-labelled DEMO dataset."""
from __future__ import annotations

import csv
import logging
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Device, DeviceSpec, PriceHistory, User
from . import datasets

log = logging.getLogger("app.seed")
settings = get_settings()


def import_devices_csv(db: Session, path) -> int:
    n = 0
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if db.get(Device, row["device_id"]):
                continue
            d = Device(id=row["device_id"], name=row["name"], brand=row["brand"], category=row["category"],
                       release_date=date.fromisoformat(row["release_date"]) if row.get("release_date") else None,
                       launch_price=float(row["launch_price"]), currency=row.get("currency") or "INR",
                       status=row.get("status") or "Active")
            for pair in filter(None, (row.get("specs") or "").split(";")):
                k, _, v = pair.partition("=")
                if k.strip() and v.strip():
                    d.specs.append(DeviceSpec(key=k.strip(), value=v.strip()))
            db.add(d)
            n += 1
    db.commit()
    return n


LEGACY_DEMO_IDS = ("LP001", "LP002", "LP003", "LP004", "LP005", "LP006", "SP001", "SP002", "SP003", "SP004", "SP005", "SP006")
LEGACY_DEMO_BRANDS = {"Acme", "Zenith", "Nova", "Orbit", "Kestrel"}


def sync_catalog(db: Session) -> dict:
    """Idempotent: adds catalogue devices that are missing and ingests only price rows that do not exist yet.
    Never updates or deletes existing devices, users, predictions or price rows, so it is safe to run repeatedly."""
    base = settings.path(settings.sample_dir)
    added = import_devices_csv(db, base / "sample_devices.csv")
    content = (base / "sample_price_history_DEMO.csv").read_bytes()
    pending = datasets.validate_only(db, content)
    if not pending.valid_rows:
        return {"devices_added": added, "history_rows_added": 0}
    ds, rep = datasets.ingest_csv(db, content, "sample_price_history_DEMO.csv", None, is_sample=True)
    return {"devices_added": added, "history_rows_added": len(rep.valid_rows), "dataset_id": ds.id}


def retire_legacy_demo(db: Session) -> dict:
    """Removes the old FICTIONAL demo devices (Acme/Zenith/Nova/Orbit/Kestrel, ids LP001-006 / SP001-006) that earlier
    versions shipped. Only devices matching BOTH the id and the fictional brand are touched, and only if all of their
    price rows are sample rows. Saved user predictions keep their snapshot (FK is SET NULL)."""
    removed = []
    for dev in db.execute(select(Device).where(Device.id.in_(LEGACY_DEMO_IDS))).scalars():
        if dev.brand not in LEGACY_DEMO_BRANDS:
            continue
        real_rows = db.execute(select(func.count()).select_from(PriceHistory)
                               .where(PriceHistory.device_id == dev.id, PriceHistory.is_sample.is_(False))).scalar_one()
        if real_rows:
            continue
        removed.append(dev.id)
        db.delete(dev)
    db.commit()
    return {"removed": removed}


def seed_sample(db: Session, force: bool = False) -> dict:
    """Loads data/sample/* when the catalogue is empty (or force=True). The price history is SYNTHETIC and flagged
    is_sample=True everywhere. Use sync_catalog() to top up an existing database without side effects."""
    if not force and db.execute(select(func.count()).select_from(Device)).scalar_one() > 0:
        return {"skipped": "catalogue is not empty"}
    return sync_catalog(db)
