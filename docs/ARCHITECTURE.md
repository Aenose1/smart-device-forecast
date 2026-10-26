# Architecture & modelling notes

```
React (Vite, TS, Tailwind, Recharts)
   │  /api (same origin via Vite proxy / Docker, or cross-origin via VITE_API_URL; no cookies)
FastAPI ── routers ── services ──► SQLAlchemy ──► PostgreSQL
                          │
                          └──► ml/pipeline.py ──► models/*.joblib  (+ model_versions rows)
```

## Request flow for a forecast
`POST /api/forecast` → auth → load device + history → find active `model_versions` row whose
`dataset_version` equals the hash of the device's current price history (else train) → forecast →
store a `predictions` row (+ `prediction_logs`) → JSON → UI chart / CSV / PDF.

## Models
* Separate pipelines: `LaptopPipeline` and `SmartphonePipeline` (own spec features and hyper-parameters). The pooled
  model only reads devices of the same category.
* Candidates per device: naive last value, linear regression, log-linear regression (exponential depreciation),
  random forest and gradient boosting on residuals of the log-linear trend, damped exponential smoothing
  (only with >= 18 monthly points), and a same-category pooled gradient-boosting model on price/launch-price ratio.
* Selection: time-aware hold-out (last max(2, 20%) observations, never shuffled), lowest RMSE wins, then refit on all data.
* Metrics: MAE, RMSE, MAPE, R² (R² only when the hold-out has >= 3 points and non-zero variance).
* Minimum data: 8 distinct price dates spanning >= 90 days. Otherwise the API returns `insufficient_history`.
* Uncertainty: approximate 95% band = ±1.96·σ·sqrt(max(1, h/H)), σ = max(hold-out RMSE, in-sample RMSE, 0.5% of price),
  H = hold-out span in months. This is a heuristic, not a calibrated predictive interval.
* Forecasts start from the date of the latest known price (`as_of`). Predictions are floored at 10% of the lowest historical price.

## Known limitations (be honest with users)
* Tree models cannot extrapolate; they are applied to detrended residuals for that reason.
* With few observations the hold-out metrics are noisy, so model selection is too.
* Forecasts ignore launches of successor devices, promotions, FX and policy changes.
* Rate limiting is in-memory per process. Use a gateway/Redis if you scale to several instances.
* Training is synchronous inside the request; for large catalogues move it to a worker queue.
