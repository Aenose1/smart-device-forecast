"""Forecasting pipelines for laptops and smartphones.

Laptop and smartphone data are NEVER mixed: each category has its own pipeline
class (own spec features, own hyper-parameters) and the pooled "category" model only
ever sees devices of the same category.

For a selected device, several candidate models are trained on a time-aware split
(the most recent observations are held out; data is never shuffled). The candidate with
the lowest hold-out RMSE is refitted on the full history and used for forecasting.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression

MIN_OBS = 8            # minimum distinct price dates needed to train
MIN_SPAN_DAYS = 90     # minimum history length
ETS_MIN_MONTHS = 18    # time-series model only considered with enough monthly data
DAYS_PER_MONTH = 30.4375
Z95 = 1.96
SEED = 42


class MLError(Exception):
    """Base class for modelling errors that are safe to show to users."""


class InsufficientDataError(MLError):
    pass


# --------------------------------------------------------------------------- specs
SPEC_ALIASES = {
    "ram_gb": ("ram", "memory"),
    "storage_gb": ("storage", "ssd", "rom", "internal storage"),
    "display_inches": ("display", "screen", "screen size", "display size"),
    "battery_mah": ("battery", "battery capacity"),
    "main_camera_mp": ("camera", "main camera", "rear camera"),
    "dedicated_gpu": ("gpu", "graphics"),
}
_NUM = re.compile(r"(\d+(?:\.\d+)?)")


def extract_spec_features(specs: dict[str, str], names: list[str]) -> dict[str, float]:
    """Turn free-text specs ('RAM': '16 GB') into numeric features. Missing -> NaN."""
    norm = {re.sub(r"[_\s]+", " ", k.strip().lower()): str(v) for k, v in specs.items()}
    out: dict[str, float] = {}
    for feat in names:
        val = math.nan
        for alias in SPEC_ALIASES[feat]:
            raw = next((v for k, v in norm.items() if k == alias or k.startswith(alias + " ")), None)
            if raw is None:
                continue
            if feat == "dedicated_gpu":
                low = raw.lower()
                val = 0.0 if (not low.strip() or any(w in low for w in ("integrated", "shared", "uhd", "iris"))) else 1.0
            else:
                m = _NUM.search(raw.replace(",", ""))
                if m:
                    val = float(m.group(1))
                    if feat == "storage_gb" and "tb" in raw.lower():
                        val *= 1000
            break
        out[feat] = val
    return out


# --------------------------------------------------------------------- pipelines
@dataclass(frozen=True)
class CategoryPipeline:
    category: str
    spec_features: tuple[str, ...]
    gbr_params: dict = field(default_factory=dict)
    rf_params: dict = field(default_factory=dict)


LaptopPipeline = CategoryPipeline(
    "Laptop",
    ("ram_gb", "storage_gb", "display_inches", "dedicated_gpu"),
    gbr_params=dict(n_estimators=150, learning_rate=0.05, max_depth=2, subsample=0.8),
    rf_params=dict(n_estimators=200, max_depth=4, min_samples_leaf=2),
)
SmartphonePipeline = CategoryPipeline(
    "Smartphone",
    ("ram_gb", "storage_gb", "display_inches", "battery_mah", "main_camera_mp"),
    gbr_params=dict(n_estimators=150, learning_rate=0.08, max_depth=2, subsample=0.8),
    rf_params=dict(n_estimators=200, max_depth=3, min_samples_leaf=2),
)
PIPELINES = {"Laptop": LaptopPipeline, "Smartphone": SmartphonePipeline}


def get_pipeline(category: str) -> CategoryPipeline:
    try:
        return PIPELINES[category]
    except KeyError:
        raise MLError(f"No forecasting pipeline exists for category '{category}'.") from None


# ------------------------------------------------------------------------ context
@dataclass
class Ctx:
    release: pd.Timestamp
    launch_ref: float
    spec_values: dict[str, float]

    def age(self, dates) -> np.ndarray:
        d = pd.DatetimeIndex(dates)
        return np.maximum((d - self.release).days.to_numpy() / DAYS_PER_MONTH, 0.0)

    def feats(self, dates) -> np.ndarray:
        d = pd.DatetimeIndex(dates)
        ang = 2 * np.pi * (d.month.to_numpy() - 1) / 12.0
        return np.column_stack([self.age(d), np.sin(ang), np.cos(ang)])


# ----------------------------------------------------------------------- candidates
class Naive:
    name = "naive_last_value"
    features = ["last observed price"]

    def fit(self, ctx, dates, y):
        self.last = float(y[-1])
        return self

    def predict(self, ctx, dates):
        return np.full(len(dates), self.last)


class Linear:
    name = "linear_regression"
    features = ["age_months"]

    def fit(self, ctx, dates, y):
        self.m = LinearRegression().fit(ctx.age(dates).reshape(-1, 1), y)
        return self

    def predict(self, ctx, dates):
        return self.m.predict(ctx.age(dates).reshape(-1, 1))


class LogLinear:
    name = "log_linear_regression"
    features = ["age_months"]

    def fit(self, ctx, dates, y):
        self.m = LinearRegression().fit(ctx.age(dates).reshape(-1, 1), np.log(y))
        return self

    def predict(self, ctx, dates):
        return np.exp(self.m.predict(ctx.age(dates).reshape(-1, 1)))


class TreeResidual:
    """Log-linear depreciation trend + tree ensemble on the (log) residuals."""

    features = ["age_months", "month_sin", "month_cos"]

    def __init__(self, kind: str, params: dict):
        self.kind, self.params = kind, params
        self.name = "random_forest_regressor" if kind == "rf" else "gradient_boosting_regressor"

    def fit(self, ctx, dates, y):
        self.base = LogLinear().fit(ctx, dates, y)
        resid = np.log(y) - np.log(self.base.predict(ctx, dates))
        cls = RandomForestRegressor if self.kind == "rf" else GradientBoostingRegressor
        self.m = cls(random_state=SEED, **self.params).fit(ctx.feats(dates), resid)
        return self

    def predict(self, ctx, dates):
        return self.base.predict(ctx, dates) * np.exp(self.m.predict(ctx.feats(dates)))


class DampedETS:
    """Damped-trend exponential smoothing on a month-start series (time-series model)."""

    name = "damped_exponential_smoothing"
    features = ["monthly price series"]

    def fit(self, ctx, dates, y):
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        s = pd.Series(y, index=pd.DatetimeIndex(dates)).resample("MS").mean().ffill()
        if len(s) < ETS_MIN_MONTHS:
            raise ValueError(f"needs >= {ETS_MIN_MONTHS} monthly points, has {len(s)}")
        self.last_month = s.index[-1]
        self.res = ExponentialSmoothing(
            s.to_numpy(), trend="add", damped_trend=True, initialization_method="estimated"
        ).fit()
        self.n = len(s)
        return self

    def predict(self, ctx, dates):
        d = pd.DatetimeIndex(dates)
        steps = (d.year - self.last_month.year) * 12 + (d.month - self.last_month.month)
        steps = np.asarray(steps)
        fc = self.res.forecast(max(1, int(steps.max())))
        fitted = self.res.fittedvalues
        out = []
        for st in steps:
            if st >= 1:
                out.append(fc[st - 1])
            else:
                out.append(fitted[max(0, self.n - 1 + int(st))])
        return np.asarray(out, dtype=float)


class PooledGBR:
    """Same-category model on price / launch-price ratio, using age + specs.

    Useful when a device has little history of its own: it borrows the depreciation
    shape of *other devices of the same category*. Only rows dated on/before the
    training cut-off are used, so no future information leaks into validation.
    """

    name = "category_pooled_gradient_boosting"

    def __init__(self, pooled: pd.DataFrame | None, spec_cols: list[str], params: dict):
        self.pooled, self.spec_cols, self.params = pooled, spec_cols, params
        self.features = ["age_months", "month_sin", "month_cos", *spec_cols]

    def _row_specs(self, ctx):
        return np.array([self.fill[c] if math.isnan(ctx.spec_values[c]) else ctx.spec_values[c] for c in self.spec_cols])

    def fit(self, ctx, dates, y):
        p = self.pooled
        if p is None or p.empty or p["device_id"].nunique() < 3:
            raise ValueError("needs >= 3 other devices of the same category with enough history")
        p = p[p["date"] <= pd.Timestamp(dates.max())]
        if p["device_id"].nunique() < 3:
            raise ValueError("not enough other-device history before the training cut-off")
        self.fill = {c: (float(p[c].median()) if p[c].notna().any() else 0.0) for c in self.spec_cols}
        Xo = p[["age", "sin", "cos", *self.spec_cols]].fillna(value=self.fill).to_numpy()
        yo = p["ratio"].to_numpy()
        spec = self._row_specs(ctx)
        Xt = np.column_stack([ctx.feats(dates), np.tile(spec, (len(dates), 1))])
        X = np.vstack([Xo, Xt])
        yy = np.concatenate([yo, np.asarray(y) / ctx.launch_ref])
        self.m = GradientBoostingRegressor(random_state=SEED, **self.params).fit(X, yy)
        self.pooled = None  # do not persist other devices' data inside the artifact
        return self

    def predict(self, ctx, dates):
        spec = self._row_specs(ctx)
        X = np.column_stack([ctx.feats(dates), np.tile(spec, (len(dates), 1))])
        return self.m.predict(X) * ctx.launch_ref


# ------------------------------------------------------------------------- metrics
def metrics(y_true, y_pred) -> dict[str, float | None]:
    y, p = np.asarray(y_true, float), np.asarray(y_pred, float)
    err = y - p
    out: dict[str, float | None] = {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
        "mape": float(np.mean(np.abs(err / y)) * 100) if np.all(y != 0) else None,
        "r2": None,
        "n_test": int(len(y)),
    }
    if len(y) >= 3:
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        if ss_tot > 0:
            out["r2"] = float(1 - np.sum(err**2) / ss_tot)
    return out


# --------------------------------------------------------------------- data prep
def prepare_history(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate multiple sources per day to one price, sorted by date."""
    d = df[["date", "price"]].copy()
    d["date"] = pd.to_datetime(d["date"])
    d = d.dropna().groupby("date", as_index=False)["price"].mean().sort_values("date")
    return d.reset_index(drop=True)


def _release_ref(release: date | None, first_obs: pd.Timestamp) -> pd.Timestamp:
    r = pd.Timestamp(release) if release else first_obs
    return min(r, first_obs)


def _build_pooled(pipeline: CategoryPipeline, others: list[dict]) -> pd.DataFrame | None:
    frames = []
    for o in others:
        h = prepare_history(pd.DataFrame(o["history"], columns=["date", "price"]))
        if len(h) < MIN_OBS:
            continue
        ref = float(o["launch_price"]) if o.get("launch_price") else float(h["price"].iloc[0])
        if ref <= 0:
            continue
        ctx = Ctx(_release_ref(o.get("release_date"), h["date"].iloc[0]), ref, {})
        f = ctx.feats(h["date"])
        specs = extract_spec_features(o.get("specs") or {}, list(pipeline.spec_features))
        fr = pd.DataFrame({"device_id": o["device_id"], "date": h["date"], "age": f[:, 0],
                           "sin": f[:, 1], "cos": f[:, 2], "ratio": h["price"] / ref})
        for c in pipeline.spec_features:
            fr[c] = specs[c]
        frames.append(fr)
    return pd.concat(frames, ignore_index=True) if frames else None


# ----------------------------------------------------------------------- training
@dataclass
class TrainedModel:
    estimator: Any
    ctx: Ctx
    category: str
    model_type: str
    metrics: dict
    candidates: list[dict]
    sigma: float
    holdout_months: float
    feature_set: dict
    n_obs: int
    first_date: pd.Timestamp
    last_date: pd.Timestamp
    last_price: float
    min_price: float


def train_device_model(category: str, device: dict, history: pd.DataFrame, others: list[dict] | None = None) -> TrainedModel:
    """Evaluate candidates with a time-aware split, refit the best on all data."""
    pipeline = get_pipeline(category)
    h = prepare_history(history)
    n = len(h)
    if n < MIN_OBS:
        raise InsufficientDataError(
            f"Only {n} distinct price date(s) available; at least {MIN_OBS} are needed to train a forecast model."
        )
    span = (h["date"].iloc[-1] - h["date"].iloc[0]).days
    if span < MIN_SPAN_DAYS:
        raise InsufficientDataError(
            f"Price history covers only {span} days; at least {MIN_SPAN_DAYS} days are needed."
        )
    if (h["price"] <= 0).any():
        raise MLError("Price history contains non-positive prices.")

    dates, y = pd.DatetimeIndex(h["date"]), h["price"].to_numpy(float)
    launch = float(device.get("launch_price") or 0) or float(y[0])
    spec_vals = extract_spec_features(device.get("specs") or {}, list(pipeline.spec_features))
    ctx = Ctx(_release_ref(device.get("release_date"), dates[0]), launch, spec_vals)
    pooled = _build_pooled(pipeline, others or [])

    def make_candidates():
        return [
            Naive(), Linear(), LogLinear(),
            TreeResidual("rf", pipeline.rf_params),
            TreeResidual("gbr", pipeline.gbr_params),
            DampedETS(),
            PooledGBR(pooled, list(pipeline.spec_features), pipeline.gbr_params),
        ]

    n_test = max(2, math.ceil(0.2 * n))
    tr, te = slice(0, n - n_test), slice(n - n_test, n)
    holdout_months = max(1.0, (dates[-1] - dates[n - n_test]).days / DAYS_PER_MONTH)

    results, scored = [], []
    for cand in make_candidates():
        row: dict[str, Any] = {"name": cand.name, "status": "ok"}
        try:
            cand.fit(ctx, dates[tr], y[tr])
            pred = np.asarray(cand.predict(ctx, dates[te]), float)
            if not np.all(np.isfinite(pred)):
                raise ValueError("non-finite predictions")
            row.update(metrics(y[te], pred))
            scored.append((row["rmse"], row["mae"], cand.name))
        except Exception as e:  # a failing candidate must not break training
            row.update(status=f"skipped: {str(e)[:120]}")
        results.append(row)
    if not scored:
        raise MLError("No candidate model could be trained on this price history.")

    best_name = min(scored)[2]
    best = next(c for c in make_candidates() if c.name == best_name).fit(ctx, dates, y)
    insample_rmse = float(np.sqrt(np.mean((y - np.asarray(best.predict(ctx, dates))) ** 2)))
    best_metrics = next(r for r in results if r["name"] == best_name)
    sigma = max(best_metrics["rmse"], insample_rmse, 0.005 * float(y[-1]))
    for r in results:
        r["selected"] = r["name"] == best_name

    return TrainedModel(
        estimator=best, ctx=ctx, category=category, model_type=best_name,
        metrics={k: best_metrics.get(k) for k in ("mae", "rmse", "mape", "r2", "n_test")}
        | {"in_sample_rmse": insample_rmse, "validation": f"time-aware hold-out of last {n_test} observations"},
        candidates=results, sigma=sigma, holdout_months=holdout_months,
        feature_set={"model_features": getattr(best, "features", []),
                     "category_spec_features": list(pipeline.spec_features)},
        n_obs=n, first_date=dates[0], last_date=dates[-1], last_price=float(y[-1]), min_price=float(y.min()),
    )


# ---------------------------------------------------------------------- forecasting
def trend_label(pct: float, stable_band: float = 1.0) -> str:
    if pct <= -stable_band:
        return "Expected decrease"
    if pct >= stable_band:
        return "Expected increase"
    return "Stable"


def forecast(model: TrainedModel, horizons_months: list[int], current_price: float | None = None) -> dict:
    """Forecast from the last observed date. Intervals are approximate 95% bands:
    sigma (max of hold-out RMSE / in-sample RMSE) scaled by sqrt(horizon / hold-out span)."""
    if not horizons_months or any(h < 1 for h in horizons_months):
        raise MLError("Forecast horizons must be positive whole months.")
    cur = float(current_price if current_price else model.last_price)
    floor = 0.1 * model.min_price
    max_h = max(horizons_months)
    origin = model.last_date

    def at(h: int):
        return origin + pd.DateOffset(months=h)

    path_dates = pd.DatetimeIndex([at(h) for h in range(1, max_h + 1)])
    path_pred = np.asarray(model.estimator.predict(model.ctx, path_dates), float)

    def band(h: int, p: float):
        s = model.sigma * math.sqrt(max(1.0, h / model.holdout_months))
        return max(p - Z95 * s, 0.0), p + Z95 * s

    clamped = False
    path = []
    for h, d, p in zip(range(1, max_h + 1), path_dates, path_pred):
        if p < floor:
            p, clamped = floor, True
        lo, hi = band(h, float(p))
        path.append({"date": d.date().isoformat(), "month": h, "predicted": round(float(p), 2),
                     "lower": round(lo, 2), "upper": round(hi, 2)})
    rows = []
    for h in sorted(set(horizons_months)):
        p = path[h - 1]
        change = p["predicted"] - cur
        pct = change / cur * 100 if cur else 0.0
        rows.append({
            "horizon_months": h, "label": f"{h // 12} year{'s' if h // 12 != 1 else ''}" if h % 12 == 0 else f"{h} months",
            "forecast_date": p["date"], "predicted_price": p["predicted"], "lower": p["lower"], "upper": p["upper"],
            "abs_change": round(change, 2), "pct_change": round(pct, 2), "trend": trend_label(pct),
        })
    return {"as_of": origin.date().isoformat(), "current_price": cur, "rows": rows, "path": path,
            "interval": {"level": 0.95, "method": "residual-based approximation (hold-out/in-sample RMSE, widened with horizon)"},
            "clamped_to_floor": clamped}
