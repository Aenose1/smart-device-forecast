from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import admin_status, require_admin
from ..errors import AppError
from ..models import Dataset, Device, DeviceSpec, ModelVersion, PredictionLog, PriceHistory, User
from ..schemas import DeviceIn, TrainIn
from ..services import datasets as ds_service
from ..services.csv_validation import CSVFormatError
from ..services.forecast_service import log_event, train_device
from ..services.reports import history_csv
from .devices import device_out, get_device_or_404

router = APIRouter(prefix="/admin", tags=["admin"])
protected = APIRouter(dependencies=[Depends(require_admin)])  # everything except /admin/status needs the admin key
settings = get_settings()
ALLOWED_EXT = {".csv"}


def _apply(device: Device, body: DeviceIn) -> None:
    device.name, device.brand, device.category = body.name.strip(), body.brand.strip(), body.category
    device.release_date, device.launch_price, device.current_price = body.release_date, body.launch_price, body.current_price
    device.currency, device.status = body.currency, body.status
    existing = {s.key: s for s in device.specs}
    for key, spec in list(existing.items()):  # merge in place: avoids unique-key clashes on update
        if key not in body.specs:
            device.specs.remove(spec)
        else:
            spec.value = body.specs[key]
    device.specs.extend(DeviceSpec(key=k, value=v) for k, v in body.specs.items() if k not in existing)


# ----------------------------------------------------------------------- devices
@protected.post("/devices", status_code=201)
def create_device(body: DeviceIn, db: Session = Depends(get_db)):
    if db.get(Device, body.device_id):
        raise AppError(409, "device_exists", f"Device ID '{body.device_id}' already exists.")
    d = Device(id=body.device_id)
    _apply(d, body)
    db.add(d)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(409, "device_exists", f"Device ID '{body.device_id}' already exists.") from None
    return device_out(d)


@protected.put("/devices/{device_id}")
def update_device(device_id: str, body: DeviceIn, db: Session = Depends(get_db)):
    d = get_device_or_404(db, device_id)
    if body.device_id != device_id:
        raise AppError(422, "id_immutable", "The device ID cannot be changed.")
    if body.category != d.category and db.execute(select(func.count()).select_from(PriceHistory).where(PriceHistory.device_id == d.id)).scalar_one():
        raise AppError(422, "category_locked", "Category cannot change once price history exists.")
    _apply(d, body)
    db.commit()
    return device_out(d)


@protected.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: str, db: Session = Depends(get_db)):
    d = get_device_or_404(db, device_id)
    db.delete(d)  # price history, specs and model versions cascade; saved predictions keep their snapshot
    db.commit()
    return Response(status_code=204)


# ---------------------------------------------------------------------- datasets
async def _read_upload(file: UploadFile) -> bytes:
    name = (file.filename or "").strip()
    if Path(name).suffix.lower() not in ALLOWED_EXT:
        raise AppError(415, "bad_extension", "Only .csv files are accepted.")
    limit = settings.max_upload_mb * 1024 * 1024
    data = bytearray()
    while chunk := await file.read(1024 * 1024):
        data.extend(chunk)
        if len(data) > limit:
            raise AppError(413, "file_too_large", f"The file exceeds the {settings.max_upload_mb} MB limit.")
    if not data:
        raise AppError(422, "empty_file", "The uploaded file is empty.")
    return bytes(data)


def _csv_error(e: CSVFormatError) -> AppError:
    return AppError(422, "invalid_csv", e.message, e.details or None)


@protected.post("/dataset/upload", status_code=201)
async def upload_dataset(file: UploadFile = File(...), is_sample: bool = Form(False), db: Session = Depends(get_db)):
    content = await _read_upload(file)
    try:
        ds, rep = ds_service.ingest_csv(db, content, file.filename or "upload.csv", None, is_sample)
    except CSVFormatError as e:
        raise _csv_error(e) from None
    return {"dataset": _dataset_out(ds), "report": {k: v for k, v in rep.summary().items() if not k.startswith("_")}}


@protected.post("/dataset/validate")
async def validate_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Dry run: full validation report, nothing is stored."""
    content = await _read_upload(file)
    try:
        rep = ds_service.validate_only(db, content)
    except CSVFormatError as e:
        raise _csv_error(e) from None
    return {k: v for k, v in rep.summary().items() if not k.startswith("_")}


def _dataset_out(d: Dataset) -> dict:
    return {"id": d.id, "filename": d.filename, "is_sample": d.is_sample, "status": d.status, "rows_total": d.rows_total,
            "rows_valid": d.rows_valid, "rows_invalid": d.rows_invalid, "rows_duplicate": d.rows_duplicate,
            "checksum": d.checksum, "created_at": d.created_at.isoformat(), "report": d.report}


@protected.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    rows = db.execute(select(Dataset).order_by(Dataset.id.desc()).limit(200)).scalars().all()
    return [_dataset_out(d) for d in rows]


@protected.get("/dataset/export")
def export_dataset(category: str | None = Query(None, pattern="^(Laptop|Smartphone)$"), device_id: str | None = Query(None, max_length=32),
                   db: Session = Depends(get_db)):
    """Processed (validated, stored) history as CSV in the standard upload format."""
    stmt = select(PriceHistory, Device).join(Device, Device.id == PriceHistory.device_id).order_by(PriceHistory.device_id, PriceHistory.date)
    if category:
        stmt = stmt.where(Device.category == category)
    if device_id:
        stmt = stmt.where(Device.id == device_id)
    import csv, io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["device_id", "device_name", "category", "date", "price", "source", "currency"])
    from ..services.reports import _safe
    for r, d in db.execute(stmt):
        w.writerow([r.device_id, _safe(d.name), d.category, r.date.isoformat(), f"{r.price:.2f}", _safe(r.source), r.currency])
    return Response(buf.getvalue().encode("utf-8"), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="processed_price_history.csv"'})


# ------------------------------------------------------------------------ models
@protected.post("/models/train")
def train_models(body: TrainIn, db: Session = Depends(get_db)):
    """Train (or retrain) models for one device, a category, or every device that has history."""
    import time
    if body.device_id:
        devices = [get_device_or_404(db, body.device_id)]
    else:
        stmt = select(Device).where(Device.id.in_(select(PriceHistory.device_id).distinct()))
        if body.category:
            stmt = stmt.where(Device.category == body.category)
        devices = db.execute(stmt.order_by(Device.id)).scalars().all()
    if not devices:
        raise AppError(404, "nothing_to_train", "No devices with price history match the request.")
    trained, failed = [], []
    for d in devices:
        t0 = time.perf_counter()
        try:
            mv, _ = train_device(db, d, None)
            trained.append({"device_id": d.id, "device_name": d.name, "model_type": mv.model_type, "metrics": mv.metrics})
            log_event("train", "ok", mv.model_type, None, d.id, started=t0)
        except AppError as e:
            db.rollback()
            failed.append({"device_id": d.id, "device_name": d.name, "reason": e.message})
            log_event("train", "error", e.message, None, d.id, started=t0)
    return {"trained": trained, "failed": failed}


@protected.get("/models")
def list_models(active_only: bool = False, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    stmt = select(ModelVersion, Device.name).join(Device, Device.id == ModelVersion.device_id)
    if active_only:
        stmt = stmt.where(ModelVersion.is_active.is_(True))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    rows = db.execute(stmt.order_by(ModelVersion.id.desc()).limit(page_size).offset((page - 1) * page_size)).all()
    return {"total": total, "items": [{
        "id": m.id, "device_id": m.device_id, "device_name": n, "category": m.category, "model_type": m.model_type,
        "trained_at": m.trained_at.isoformat(), "dataset_version": m.dataset_version, "n_observations": m.n_observations,
        "metrics": m.metrics, "candidates": m.candidates, "feature_set": m.feature_set, "is_active": m.is_active}
        for m, n in rows]}


@protected.get("/prediction-logs")
def prediction_logs(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), status: str | None = Query(None, pattern="^(ok|error)$"),
                    db: Session = Depends(get_db)):
    stmt = select(PredictionLog, User.email).outerjoin(User, User.id == PredictionLog.user_id)
    if status:
        stmt = stmt.where(PredictionLog.status == status)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    rows = db.execute(stmt.order_by(PredictionLog.id.desc()).limit(page_size).offset((page - 1) * page_size)).all()
    return {"total": total, "items": [{
        "id": l.id, "created_at": l.created_at.isoformat(), "event": l.event, "status": l.status, "message": l.message,
        "device_id": l.device_id, "prediction_id": l.prediction_id, "user": ("visitor" if email and email.endswith("@visitors.invalid") else email),
        "duration_ms": l.duration_ms}
        for l, email in rows]}


@protected.get("/overview")
def overview(db: Session = Depends(get_db)):
    c = lambda m, *w: db.execute(select(func.count()).select_from(m).where(*w)).scalar_one()  # noqa: E731
    return {"users": c(User), "devices": c(Device), "datasets": c(Dataset), "history_records": c(PriceHistory),
            "active_models": c(ModelVersion, ModelVersion.is_active.is_(True)),
            "devices_without_history": db.execute(select(func.count()).select_from(Device).where(
                ~Device.id.in_(select(PriceHistory.device_id).distinct()))).scalar_one(),
            "errors_last_100_logs": db.execute(select(func.count()).select_from(
                select(PredictionLog.status).order_by(PredictionLog.id.desc()).limit(100).subquery()).where(text_status())).scalar_one()}


def text_status():
    from sqlalchemy import literal_column
    return literal_column("status") == "error"


@router.get("/status")
def admin_status_endpoint(request: Request):
    """Tells the admin pages how administration is configured and whether the supplied key is accepted.
    Reveals nothing secret: mode is 'key', 'open' (demo only, never in production) or 'disabled'."""
    mode, ok = admin_status(request)
    return {"mode": mode, "authorized": ok}


router.include_router(protected)
