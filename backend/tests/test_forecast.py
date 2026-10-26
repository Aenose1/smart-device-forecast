import pandas as pd
import numpy as np
from datetime import date

from ml import pipeline as ml

from .conftest import add_device


def test_forecast_pipeline_end_to_end(user):
    add_device(months=30, decay=0.015)
    r = user.post("/api/forecast", json={"device_id": "LP001"})
    assert r.status_code == 201, r.text
    j = r.json()
    assert [x["label"] for x in j["results"]] == ["1 year", "2 years", "3 years"]
    prices = [x["predicted_price"] for x in j["results"]]
    assert prices[0] > prices[1] > prices[2] > 0                      # depreciating device
    assert all(x["trend"] == "Expected decrease" and x["lower"] <= x["predicted_price"] <= x["upper"] for x in j["results"])
    assert j["results"][0]["pct_change"] == round((prices[0] - j["current_price"]) / j["current_price"] * 100, 2)
    assert "may differ from actual market prices" in j["disclaimer"]
    assert len(j["path"]) == 36 and j["model_info"]["metrics"]["rmse"] is not None
    assert j["model_info"]["model_type"] in {c["name"] for c in j["model_info"]["candidates"]}
    # persisted and visible in history
    assert user.get(f"/api/predictions/{j['id']}").json()["id"] == j["id"]
    assert user.get("/api/predictions").json()["total"] == 1


def test_model_is_reused_until_data_changes(user, admin):
    from backend.app.db import SessionLocal
    from backend.app.models import ModelVersion, PriceHistory
    add_device(months=30)
    user.post("/api/forecast", json={"device_id": "LP001"})
    user.post("/api/forecast", json={"device_id": "LP001"})
    with SessionLocal() as db:
        assert db.query(ModelVersion).count() == 1
        db.add(PriceHistory(device_id="LP001", date=date(2026, 9, 1), price=60000, source="new", currency="INR"))
        db.commit()
    user.post("/api/forecast", json={"device_id": "LP001"})
    with SessionLocal() as db:
        assert db.query(ModelVersion).count() == 2 and db.query(ModelVersion).filter_by(is_active=True).count() == 1


def test_configurable_horizon(user):
    add_device(months=30)
    j = user.post("/api/forecast", json={"device_id": "LP001", "years": 2}).json()
    assert [x["horizon_months"] for x in j["results"]] == [12, 24]
    assert user.post("/api/forecast", json={"device_id": "LP001", "years": 9}).status_code == 422


def test_predict_single_horizon(user):
    add_device(months=30)
    r = user.post("/api/predict", json={"device_id": "LP001", "months": 6})
    assert r.status_code == 201 and len(r.json()["results"]) == 1 and r.json()["results"][0]["horizon_months"] == 6
    assert user.post("/api/predict", json={"device_id": "LP001", "months": 0}).status_code == 422
    assert user.post("/api/predict", json={"device_id": "LP001", "months": 999}).status_code == 422


def test_error_paths(user, admin):
    from backend.app.db import SessionLocal
    from backend.app.models import Device
    assert user.post("/api/forecast", json={"device_id": "NOPE"}).status_code == 404
    with SessionLocal() as db:
        db.add(Device(id="EMPTY1", name="Empty", brand="B", category="Laptop", launch_price=1000, currency="INR"))
        db.commit()
    r = user.post("/api/forecast", json={"device_id": "EMPTY1"})
    assert r.status_code == 422 and r.json()["code"] == "no_price_history"
    add_device("LP009", "Short", months=4)
    r = user.post("/api/forecast", json={"device_id": "LP009"})
    assert r.status_code == 422 and r.json()["code"] == "insufficient_history" and "at least" in r.json()["detail"]
    assert user.post("/api/forecast", json={}).status_code == 422
    logs = admin.get("/api/admin/prediction-logs", params={"status": "error"}).json()
    assert logs["total"] >= 2 and all("Traceback" not in l["message"] for l in logs["items"])


def test_sample_data_is_flagged(user):
    add_device(months=30, sample=True)
    j = user.post("/api/forecast", json={"device_id": "LP001"}).json()
    assert j["is_sample"] and any("SAMPLE" in w for w in j["warnings"])


def test_pdf_and_csv_downloads(user):
    add_device(months=30)
    pid = user.post("/api/forecast", json={"device_id": "LP001"}).json()["id"]
    c = user.get(f"/api/predictions/{pid}/csv")
    assert c.status_code == 200 and "device_3_year_forecast.csv" in c.headers["content-disposition"]
    lines = c.content.decode("utf-8-sig").strip().splitlines()
    assert lines[0] == "Device,Category,Current Price,Forecast Date,Forecast Year,Predicted Price,Percentage Change,Trend"
    assert len(lines) == 4 and "Year" not in lines[1].split(",")[0]
    p = user.get(f"/api/predictions/{pid}/pdf")
    assert p.status_code == 200 and p.content[:5] == b"%PDF-" and len(p.content) > 5000


def test_predictions_are_private_to_each_user(user, user2):
    add_device(months=30)
    pid = user.post("/api/forecast", json={"device_id": "LP001"}).json()["id"]
    assert user2.get("/api/predictions").json()["total"] == 0
    for suffix in ("", "/csv", "/pdf"):
        assert user2.get(f"/api/predictions/{pid}{suffix}").status_code == 404
    assert user.get(f"/api/predictions/{pid}").status_code == 200


def test_separate_category_pipelines(user):
    add_device("LP001", "L", "Laptop", months=30)
    for i in range(2, 5):
        add_device(f"LP00{i}", f"L{i}", "Laptop", months=30, decay=0.01 + i / 500)
    add_device("SP001", "P", "Smartphone", months=30, decay=0.03)
    lap = user.post("/api/forecast", json={"device_id": "LP001"}).json()
    ph = user.post("/api/forecast", json={"device_id": "SP001"}).json()
    assert lap["model_info"]["category"] == "Laptop" and ph["model_info"]["category"] == "Smartphone"
    assert lap["model_info"]["feature_set"]["category_spec_features"] == list(ml.LaptopPipeline.spec_features)
    assert ph["model_info"]["feature_set"]["category_spec_features"] == list(ml.SmartphonePipeline.spec_features)
    names = {c["name"]: c["status"] for c in lap["model_info"]["candidates"]}
    assert names["category_pooled_gradient_boosting"] == "ok"        # pooled model only used same-category peers


# ---- pure ML unit tests ------------------------------------------------------------------
def _series(n, decay=0.02, seed=0):
    rng = np.random.default_rng(seed)
    d = pd.date_range("2024-01-01", periods=n, freq="MS")
    return pd.DataFrame({"date": d, "price": 100000 * np.exp(-decay * np.arange(n)) * (1 + rng.normal(0, 0.005, n))})


def test_time_aware_split_and_metrics():
    m = ml.train_device_model("Smartphone", {"launch_price": 100000, "release_date": date(2024, 1, 1), "specs": {}}, _series(30))
    assert m.metrics["n_test"] == 6 and "time-aware" in m.metrics["validation"]
    assert m.metrics["mae"] >= 0 and m.metrics["rmse"] >= m.metrics["mae"] and m.metrics["mape"] is not None
    assert m.model_type != "naive_last_value"            # a clear downward trend must beat "no change"
    assert sum(c["selected"] for c in m.candidates) == 1


def test_insufficient_data():
    import pytest
    with pytest.raises(ml.InsufficientDataError):
        ml.train_device_model("Laptop", {"launch_price": 1, "specs": {}}, _series(5))
    short = _series(10); short["date"] = pd.date_range("2026-01-01", periods=10, freq="D")
    with pytest.raises(ml.InsufficientDataError, match="days"):
        ml.train_device_model("Laptop", {"launch_price": 1, "specs": {}}, short)


def test_spec_extraction():
    f = ml.extract_spec_features({"RAM": "16 GB", "Storage": "1 TB", "GPU": "Integrated Iris Xe", "display": "15.6 inch"},
                                 list(ml.LaptopPipeline.spec_features))
    assert f["ram_gb"] == 16 and f["storage_gb"] == 1000 and f["dedicated_gpu"] == 0 and f["display_inches"] == 15.6
    assert np.isnan(ml.extract_spec_features({}, ["battery_mah"])["battery_mah"])
