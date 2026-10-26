"""Ingestion of validated price CSVs into the database."""
from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Dataset, Device, PriceHistory
from .csv_validation import ValidationReport, validate_price_csv

settings = get_settings()


def device_lookup(db: Session) -> dict[str, dict]:
    rows = db.execute(select(Device.id, Device.name, Device.category, Device.currency)).all()
    return {r.id: {"name": r.name, "category": r.category, "currency": r.currency} for r in rows}


def existing_keys(db: Session) -> set:
    return {(r.device_id, r.date, r.source) for r in db.execute(
        select(PriceHistory.device_id, PriceHistory.date, PriceHistory.source))}


def validate_only(db: Session, content: bytes) -> ValidationReport:
    return validate_price_csv(content, device_lookup(db), existing_keys(db))


def ingest_csv(db: Session, content: bytes, filename: str, user_id: int | None, is_sample: bool) -> tuple[Dataset, ValidationReport]:
    rep = validate_only(db, content)  # raises CSVFormatError for file-level problems
    up = settings.path(settings.uploads_dir)
    up.mkdir(parents=True, exist_ok=True)
    stored = up / f"{uuid.uuid4().hex}.csv"
    stored.write_bytes(content)
    summ = rep.summary()
    ds = Dataset(
        filename=Path(filename).name[:255], stored_path=str(stored), checksum=hashlib.sha256(content).hexdigest(),
        uploaded_by=user_id, is_sample=is_sample, rows_total=rep.total_rows, rows_valid=len(rep.valid_rows),
        rows_invalid=summ["invalid_rows"], rows_duplicate=rep.duplicates_in_file + rep.duplicates_existing,
        status="processed" if rep.valid_rows else "rejected",
        report={k: v for k, v in summ.items() if not k.startswith("_")},
    )
    db.add(ds)
    db.flush()
    db.add_all(PriceHistory(dataset_id=ds.id, is_sample=is_sample, **r) for r in rep.valid_rows)
    db.commit()
    return ds, rep
