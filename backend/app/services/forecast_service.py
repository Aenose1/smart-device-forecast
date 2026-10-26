"""Glue between database, ML pipeline and persisted predictions."""
from __future__ import annotations

import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ml import pipeline as ml

from ..config import get_settings
from ..db import SessionLocal
from ..errors import AppError
from ..models import Device, ModelVersion, Prediction, PredictionLog, PriceHistory
from ..schemas import specs_to_dict
from .history import compute_stats, daily_series

log = logging.getLogger("app.forecast")
settings = get_settings()
DISCLAIMER = ("This prediction is based on historical price patterns and may differ from actual market prices. "
              "It is an estimate, not a guarantee.")


# ------------------------------------------------------------------ data access
def load_history(db: Session, device_id: str) -> list[tuple]:
    return [(r.date, r.price, r.is_sample) for r in db.execute(
        select(PriceHistory.date, PriceHistory.price, PriceHistory.is_sample)
        .where(PriceHistory.device_id == device_id).order_by(PriceHistory.date))]


def dataset_version(history: pd.DataFrame) -> str:
    h = ml.prepare_history(history)
    raw = "|".join(f"{d.date()}:{p:.4f}" for d, p in zip(h["date"], h["price"]))
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def _device_dict(device: Device) -> dict:
    return {"device_id": device.id, "release_date": device.release_date,
            "launch_price": device.launch_price, "specs": specs_to_dict(device)}


def _others(db: Session, device: Device, limit: int = 200) -> list[dict]:
    """Same-category devices only (laptops are never mixed with smartphones)."""
    peers = db.execute(select(Device).where(Device.category == device.category, Device.id != device.id)).scalars().all()
    out = []
    for p in peers[:limit]:
        h = [(r.date, r.price) for r in db.execute(select(PriceHistory.date, PriceHistory.price).where(PriceHistory.device_id == p.id))]
        if len(h) >= ml.MIN_OBS:
            out.append({**_device_dict(p), "history": h})
    return out


def _safe_artifact(path: str) -> Path:
    base = settings.path(settings.models_dir).resolve()
    p = Path(path).resolve()
    if base not in p.parents:
        raise AppError(500, "model_error", "Stored model path is invalid.")
    return p


# --------------------------------------------------------------------- logging
def log_event(event: str, status: str, message: str = "", user_id: int | None = None, device_id: str | None = None,
              prediction_id: int | None = None, started: float | None = None) -> None:
    """Writes in its own session so failures are logged even when the request transaction rolled back."""
    try:
        with SessionLocal() as s:
            s.add(PredictionLog(user_id=user_id, device_id=device_id, prediction_id=prediction_id, event=event,
                                status=status, message=message[:1000],
                                duration_ms=int((time.perf_counter() - started) * 1000) if started else 0))
            s.commit()
    except Exception:  # logging must never break the request
        log.exception("Could not write prediction log")


# -------------------------------------------------------------------- training
def train_device(db: Session, device: Device, trained_by: int | None = None) -> tuple[ModelVersion, ml.TrainedModel]:
    rows = load_history(db, device.id)
    if not rows:
        raise AppError(422, "no_price_history", f"No historical prices exist for '{device.name}'. Upload price history first.")
    df = pd.DataFrame([(d, p) for d, p, _ in rows], columns=["date", "price"])
    try:
        model = ml.train_device_model(device.category, _device_dict(device), df, _others(db, device))
    except ml.InsufficientDataError as e:
        raise AppError(422, "insufficient_history", str(e)) from None
    except ml.MLError as e:
        raise AppError(422, "training_failed", str(e)) from None
    except Exception:
        log.exception("Training failed for %s", device.id)
        raise AppError(500, "training_failed", "Model training failed unexpectedly. The error was logged.") from None

    ver = dataset_version(df)
    mdir = settings.path(settings.models_dir)
    mdir.mkdir(parents=True, exist_ok=True)
    path = mdir / f"{device.id}_{ver}_{uuid.uuid4().hex[:8]}.joblib"
    joblib.dump(model, path)
    db.execute(update(ModelVersion).where(ModelVersion.device_id == device.id).values(is_active=False))
    mv = ModelVersion(device_id=device.id, category=device.category, model_type=model.model_type,
                      dataset_version=ver, n_observations=model.n_obs, metrics=model.metrics,
                      candidates=model.candidates, feature_set=model.feature_set, artifact_path=str(path),
                      is_active=True, trained_by=trained_by)
    db.add(mv)
    db.commit()
    return mv, model


def get_or_train(db: Session, device: Device, user_id: int | None = None) -> tuple[ModelVersion, ml.TrainedModel]:
    rows = load_history(db, device.id)
    if not rows:
        raise AppError(422, "no_price_history", f"No historical prices exist for '{device.name}'. Upload price history first.")
    ver = dataset_version(pd.DataFrame([(d, p) for d, p, _ in rows], columns=["date", "price"]))
    mv = db.execute(select(ModelVersion).where(ModelVersion.device_id == device.id, ModelVersion.is_active.is_(True))
                    .order_by(ModelVersion.id.desc())).scalars().first()
    if mv and mv.dataset_version == ver:
        try:
            return mv, joblib.load(_safe_artifact(mv.artifact_path))
        except Exception:
            log.warning("Model artifact for %s unreadable; retraining", device.id)
    return train_device(db, device, user_id)


# ------------------------------------------------------------------ predictions
def create_prediction(db: Session, user_id: int, device: Device, horizons_months: list[int], kind: str) -> Prediction:
    started = time.perf_counter()
    try:
        rows = load_history(db, device.id)
        mv, model = get_or_train(db, device, user_id)
        result = ml.forecast(model, horizons_months)
        pairs = [(d, p) for d, p, _ in rows]
        stats = compute_stats(pairs)
        is_sample = any(s for *_, s in rows)
        warnings = []
        age_days = (datetime.now(timezone.utc).date() - model.last_date.date()).days
        if age_days > 90:
            warnings.append(f"The latest known price is from {model.last_date.date()} ({age_days} days ago); forecasts are measured from that date.")
        if is_sample:
            warnings.append("This device's history includes SAMPLE/DEMO data. Results are for demonstration only.")
        if result["clamped_to_floor"]:
            warnings.append("Some predicted values were limited to 10% of the lowest historical price.")
        if model.n_obs < 24:
            warnings.append(f"Only {model.n_obs} historical price dates were available, so uncertainty is high.")
        daily = [(d.isoformat(), round(p, 2)) for d, p in daily_series(pairs)]
        pred = Prediction(
            user_id=user_id, device_id=device.id, model_version_id=mv.id, kind=kind, device_name=device.name,
            brand=device.brand, category=device.category, currency=device.currency, current_price=result["current_price"],
            as_of=model.last_date.date(), horizons=sorted(set(horizons_months)), results=result["rows"],
            path=result["path"], history=daily, stats=stats,
            model_info={"model_type": mv.model_type, "trained_at": mv.trained_at.isoformat() if mv.trained_at else None,
                        "dataset_version": mv.dataset_version, "metrics": mv.metrics, "candidates": mv.candidates,
                        "feature_set": mv.feature_set, "n_observations": mv.n_observations, "category": mv.category,
                        "interval": result["interval"]},
            warnings=warnings, is_sample=is_sample)
        db.add(pred)
        db.commit()
    except AppError as e:
        db.rollback()
        log_event(kind, "error", e.message, user_id, device.id, started=started)
        raise
    except ml.MLError as e:
        db.rollback()
        log_event(kind, "error", str(e), user_id, device.id, started=started)
        raise AppError(422, "forecast_failed", str(e)) from None
    except Exception as e:
        db.rollback()
        log.exception("Forecast failed for %s", device.id)
        log_event(kind, "error", f"{type(e).__name__}: {e}", user_id, device.id, started=started)
        raise AppError(500, "forecast_failed", "The forecast could not be generated. The error was logged.") from None
    log_event(kind, "ok", f"{mv.model_type}; horizons={pred.horizons}", user_id, device.id, pred.id, started)
    return pred


def serialize_prediction(p: Prediction, full: bool = True) -> dict:
    last = p.results[-1] if p.results else None
    out = {
        "id": p.id, "kind": p.kind, "device_id": p.device_id, "device_name": p.device_name, "brand": p.brand,
        "category": p.category, "currency": p.currency, "current_price": p.current_price,
        "as_of": p.as_of.isoformat(), "horizons": p.horizons, "results": p.results,
        "overall_trend": last["trend"] if last else None, "overall_pct_change": last["pct_change"] if last else None,
        "model_type": p.model_info.get("model_type"), "is_sample": p.is_sample, "created_at": p.created_at.isoformat(),
        "disclaimer": DISCLAIMER,
    }
    if full:
        out.update(path=p.path, history=p.history, stats=p.stats, model_info=p.model_info, warnings=p.warnings)
    return out
