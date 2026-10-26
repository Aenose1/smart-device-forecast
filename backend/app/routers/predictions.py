from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import find_visitor, get_visitor
from ..errors import AppError
from ..models import Device, Prediction, User
from ..ratelimit import limiter
from ..schemas import ForecastIn, PredictIn
from ..services import reports
from ..services.forecast_service import create_prediction, serialize_prediction
from .devices import get_device_or_404

router = APIRouter(tags=["predictions"])
settings = get_settings()


@router.post("/predict", status_code=201, dependencies=[Depends(limiter("forecast", 30, 60))])
def predict(body: PredictIn, db: Session = Depends(get_db), user: User = Depends(get_visitor)):
    """Single estimated price for one horizon given in months."""
    device = get_device_or_404(db, body.device_id)
    if body.months > settings.max_forecast_years * 12:
        raise AppError(422, "invalid_horizon", f"Horizon cannot exceed {settings.max_forecast_years} years ({settings.max_forecast_years * 12} months).")
    return serialize_prediction(create_prediction(db, user.id, device, [body.months], "predict"))


@router.post("/forecast", status_code=201, dependencies=[Depends(limiter("forecast", 30, 60))])
def forecast(body: ForecastIn, db: Session = Depends(get_db), user: User = Depends(get_visitor)):
    """Yearly forecast (1..N years). The horizon is configurable; default 3 years."""
    device = get_device_or_404(db, body.device_id)
    if body.years > settings.max_forecast_years:
        raise AppError(422, "invalid_horizon", f"Forecast horizon cannot exceed {settings.max_forecast_years} years.")
    return serialize_prediction(create_prediction(db, user.id, device, [12 * y for y in range(1, body.years + 1)], "forecast"))


def _own(db: Session, user: User | None, pid: int) -> Prediction:
    p = db.get(Prediction, pid)
    if not p or user is None or p.user_id != user.id:  # other visitors' records look non-existent
        raise AppError(404, "prediction_not_found", "Prediction not found.")
    return p


@router.get("/predictions")
def list_predictions(device_id: str | None = Query(None, max_length=32), page: int = Query(1, ge=1),
                     page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User | None = Depends(find_visitor)):
    if user is None:  # this browser has not made any forecast yet
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    stmt = select(Prediction).where(Prediction.user_id == user.id)
    if device_id:
        stmt = stmt.where(Prediction.device_id == device_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    rows = db.execute(stmt.order_by(Prediction.created_at.desc(), Prediction.id.desc())
                      .limit(page_size).offset((page - 1) * page_size)).scalars().all()
    return {"items": [serialize_prediction(p, full=False) for p in rows], "total": total, "page": page, "page_size": page_size}


@router.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: int, db: Session = Depends(get_db), user: User | None = Depends(find_visitor)):
    return serialize_prediction(_own(db, user, prediction_id))


@router.get("/predictions/{prediction_id}/csv")
def prediction_csv(prediction_id: int, db: Session = Depends(get_db), user: User | None = Depends(find_visitor)):
    p = _own(db, user, prediction_id)
    return Response(reports.prediction_csv(p), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{reports.csv_filename(p)}"'})


@router.get("/predictions/{prediction_id}/pdf")
def prediction_pdf(prediction_id: int, db: Session = Depends(get_db), user: User | None = Depends(find_visitor)):
    p = _own(db, user, prediction_id)
    device = db.get(Device, p.device_id) if p.device_id else None
    return Response(reports.prediction_pdf(p, device), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="forecast_{p.device_id or p.id}_{p.id}.pdf"'})
