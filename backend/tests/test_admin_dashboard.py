from sqlalchemy import func, select

from backend.app.db import SessionLocal
from backend.app.models import Device, PriceHistory, Prediction

from .conftest import add_device, make_client

PAYLOAD = {"device_id": "LP100", "name": "New Laptop", "brand": "Acme", "category": "Laptop", "release_date": "2025-01-01",
           "launch_price": 90000, "currency": "inr", "status": "Active", "specs": {"RAM": "16 GB", "Empty": ""}}


def test_device_crud(admin, user):
    r = admin.post("/api/admin/devices", json=PAYLOAD)
    assert r.status_code == 201 and r.json()["currency"] == "INR" and r.json()["specs"] == {"RAM": "16 GB"}
    assert admin.post("/api/admin/devices", json=PAYLOAD).status_code == 409
    assert user.get("/api/devices/LP100").status_code == 200       # visible to normal users
    upd = {**PAYLOAD, "name": "Renamed", "specs": {"RAM": "32 GB", "Storage": "1 TB"}}
    r = admin.put("/api/admin/devices/LP100", json=upd)
    assert r.json()["name"] == "Renamed" and r.json()["specs"] == {"RAM": "32 GB", "Storage": "1 TB"}
    assert admin.put("/api/admin/devices/LP100", json={**upd, "device_id": "OTHER1"}).status_code == 422
    assert admin.delete("/api/admin/devices/LP100").status_code == 204
    assert admin.get("/api/admin/devices/LP100").status_code in (404, 405)
    assert user.get("/api/devices/LP100").status_code == 404


def test_device_validation(admin):
    for bad in ({"device_id": "bad id!"}, {"launch_price": -1}, {"category": "Tablet"}, {"currency": "RUPEES"}):
        assert admin.post("/api/admin/devices", json={**PAYLOAD, **bad}).status_code == 422


def test_delete_cascades_but_keeps_user_prediction_history(admin, user):
    add_device(months=30)
    pid = user.post("/api/forecast", json={"device_id": "LP001"}).json()["id"]
    assert admin.delete("/api/admin/devices/LP001").status_code == 204
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(PriceHistory)) == 0
        assert db.get(Prediction, pid).device_id is None
    j = user.get(f"/api/predictions/{pid}").json()
    assert j["device_name"] == "Test Laptop X"
    assert user.get(f"/api/predictions/{pid}/pdf").status_code == 200


def test_admin_training_and_model_metrics(admin):
    add_device("LP001", months=30)
    add_device("LP002", "Short", months=3)
    r = admin.post("/api/admin/models/train", json={}).json()
    assert [t["device_id"] for t in r["trained"]] == ["LP001"] and r["failed"][0]["device_id"] == "LP002"
    models = admin.get("/api/admin/models").json()
    assert models["total"] == 1 and models["items"][0]["metrics"]["rmse"] is not None and models["items"][0]["is_active"]
    assert admin.post("/api/admin/models/train", json={"device_id": "NOPE"}).status_code == 404
    assert admin.get("/api/admin/overview").json()["active_models"] == 1
    logs = admin.get("/api/admin/prediction-logs").json()
    assert {l["event"] for l in logs["items"]} == {"train"}


def test_dashboard(user):
    add_device("LP001", months=12, decay=0.03)
    add_device("SP001", "Phone", "Smartphone", months=12, decay=-0.01)
    d = user.get("/api/dashboard").json()
    assert (d["total_devices"], d["laptops"], d["smartphones"], d["history_records"]) == (2, 1, 1, 24)
    assert d["top_decreases"][0]["id"] == "LP001" and d["top_increases"][0]["id"] == "SP001"
    assert d["average_price_change"] is not None and d["recent_predictions"] == [] and d["records_by_month"]


def test_health_and_unknown_api_path(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/nothing-here").status_code == 404


def test_forecast_endpoint_is_rate_limited(client, monkeypatch):
    from backend.app.config import get_settings
    from backend.app.ratelimit import reset_limits
    monkeypatch.setattr(get_settings(), "rate_limit_enabled", True)
    reset_limits()
    try:
        c = make_client("visitor-rate-0123456789")
        codes = [c.post("/api/forecast", json={"device_id": "NOPE"}).status_code for _ in range(32)]
        assert codes[:30] == [404] * 30 and codes[30] == 429
    finally:
        reset_limits()
