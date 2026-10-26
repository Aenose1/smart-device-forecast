"""No-login access model: public features need nothing, administration needs ADMIN_API_KEY, CORS is explicit."""
import re

import pytest
from fastapi import Request

from backend.app.config import Settings, get_settings, normalize_database_url
from backend.app.ratelimit import client_ip

from .conftest import ADMIN_KEY, add_device, make_client

settings = get_settings()
VERCEL = "https://smart-device-forcast-1.vercel.app"


# ------------------------------------------------------------- everything normal is public
def test_no_login_endpoints_exist(client):
    for path in ("/api/auth/login", "/api/auth/register", "/api/auth/logout", "/api/auth/me"):
        assert make_client().post(path, json={}).status_code in (404, 405)


def test_public_features_work_with_no_cookie_token_or_header(client):
    add_device("LP001", "Test Laptop X", months=30)
    add_device("LP002", "Test Laptop Y", months=30, decay=0.01)
    c = make_client()
    assert c.get("/api/health").status_code == 200
    assert c.get("/api/devices").json()["total"] == 2
    assert c.get("/api/devices/LP001").json()["name"] == "Test Laptop X"
    assert c.get("/api/devices/LP001/history").json()["stats"]["records"] == 30
    assert c.get("/api/devices/LP001/history", params={"format": "csv"}).status_code == 200
    assert c.get("/api/dashboard").status_code == 200 and c.get("/api/predictions").json()["total"] == 0
    r = c.post("/api/forecast", json={"device_id": "LP001", "years": 3})
    assert r.status_code == 201 and len(r.json()["results"]) == 3 and r.json()["model_info"]["metrics"]["rmse"] is not None
    assert c.post("/api/predict", json={"device_id": "LP002", "months": 6}).status_code == 201
    pid = r.json()["id"]
    assert c.get(f"/api/predictions/{pid}/csv").status_code == 200 and c.get(f"/api/predictions/{pid}/pdf").content[:5] == b"%PDF-"


# ------------------------------------------------------ anonymous per-browser history
def test_history_is_kept_per_browser_and_not_shared(client):
    add_device(months=30)
    a, b = make_client("browser-a-0123456789"), make_client("browser-b-0123456789")
    pid = a.post("/api/forecast", json={"device_id": "LP001"}).json()["id"]
    assert a.get("/api/predictions").json()["total"] == 1 and a.get(f"/api/predictions/{pid}").status_code == 200
    assert b.get("/api/predictions").json()["total"] == 0
    for suffix in ("", "/csv", "/pdf"):
        assert b.get(f"/api/predictions/{pid}{suffix}").status_code == 404
    assert a.get("/api/dashboard").json()["recent_predictions"][0]["id"] == pid
    assert b.get("/api/dashboard").json()["recent_predictions"] == []


def test_invalid_visitor_id_is_rejected_cleanly(client):
    add_device(months=30)
    r = make_client("short").post("/api/forecast", json={"device_id": "LP001"})
    assert r.status_code == 400 and r.json()["code"] == "invalid_visitor_id"
    assert make_client("x" * 65).get("/api/predictions").status_code == 400
    assert make_client("bad id with spaces!!").get("/api/predictions").status_code == 400


def test_visitor_rows_are_not_real_accounts(client):
    from backend.app.db import SessionLocal
    from backend.app.models import User
    add_device(months=30)
    make_client("browser-c-0123456789").post("/api/forecast", json={"device_id": "LP001"})
    with SessionLocal() as db:
        u = db.query(User).one()
        assert u.email.endswith("@visitors.invalid") and u.password_hash == "!" and u.role == "user"


def test_errors_are_graceful_without_login(client):
    add_device("LP009", "Short", months=4)
    c = make_client("browser-d-0123456789")
    assert c.post("/api/forecast", json={"device_id": "NOPE"}).status_code == 404
    r = c.post("/api/forecast", json={"device_id": "LP009"})
    assert r.status_code == 422 and r.json()["code"] == "insufficient_history"
    assert c.post("/api/forecast", json={"device_id": "LP009", "years": 99}).status_code == 422


# ----------------------------------------------------------------- administration stays protected
ADMIN_GET = ["/api/admin/datasets", "/api/admin/models", "/api/admin/prediction-logs", "/api/admin/overview", "/api/admin/dataset/export"]


def test_admin_requires_the_key(client):
    anon, wrong, ok = make_client(), TestClient_with_key("not-the-key-0123456789"), make_client(admin=True)
    for path in ADMIN_GET:
        assert anon.get(path).status_code == 401 and wrong.get(path).status_code == 401, path
        assert ok.get(path).status_code == 200, path
    body = {"device_id": "PH900", "name": "T", "brand": "B", "category": "Smartphone", "launch_price": 1000, "specs": {}}
    assert anon.post("/api/admin/devices", json=body).status_code == 401
    assert anon.post("/api/admin/models/train", json={}).status_code == 401
    assert anon.delete("/api/admin/devices/PH900").status_code == 401
    assert ok.post("/api/admin/devices", json=body).status_code == 201


def TestClient_with_key(key):
    from fastapi.testclient import TestClient
    from backend.app.main import app
    return TestClient(app, headers={"X-Admin-Key": key})


def test_admin_status_reveals_mode_not_secrets(client):
    assert make_client().get("/api/admin/status").json() == {"mode": "key", "authorized": False}
    r = make_client(admin=True).get("/api/admin/status")
    assert r.json() == {"mode": "key", "authorized": True} and ADMIN_KEY not in r.text


def test_admin_is_disabled_without_a_key(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "")
    r = make_client().get("/api/admin/datasets")
    assert r.status_code == 403 and r.json()["code"] == "admin_disabled"
    assert make_client().get("/api/admin/status").json() == {"mode": "disabled", "authorized": False}


def test_open_admin_demo_mode_works_locally_but_never_in_production(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "")
    monkeypatch.setattr(settings, "allow_open_admin", True)
    assert make_client().get("/api/admin/datasets").status_code == 200            # development: demo switch honoured
    monkeypatch.setattr(settings, "environment", "production")
    assert make_client().get("/api/admin/datasets").status_code == 403            # production: ignored
    monkeypatch.setenv("RENDER", "true"); monkeypatch.setattr(settings, "environment", "development")
    assert make_client().get("/api/admin/datasets").status_code == 403            # Render is detected as production


def test_short_admin_key_is_rejected_at_startup():
    with pytest.raises(Exception, match="at least 16"):
        Settings(_env_file=None, database_url="sqlite://", admin_api_key="short")


# -------------------------------------------------------------------------------- CORS
def preflight(c, origin, method="POST", headers="content-type,x-visitor-id", path="/api/forecast"):
    return c.options(path, headers={"Origin": origin, "Access-Control-Request-Method": method, "Access-Control-Request-Headers": headers})


def test_cors_allows_the_vercel_site_and_local_dev_only(client):
    c = make_client()
    for origin in (VERCEL, "http://localhost:5173", "http://127.0.0.1:5173"):
        r = preflight(c, origin)
        assert r.status_code == 200 and r.headers["access-control-allow-origin"] == origin, origin
        assert "x-visitor-id" in r.headers["access-control-allow-headers"].lower()
        assert "access-control-allow-credentials" not in r.headers            # no cookies are used, so credentials are never allowed
    for origin in ("https://evil.example.com", "https://smart-device-forcast-1.vercel.app.evil.com", "http://smart-device-forcast-1.vercel.app"):
        r = preflight(c, origin)
        assert "access-control-allow-origin" not in r.headers, origin


def test_cors_rejects_unneeded_methods_and_headers(client):
    r = preflight(make_client(), VERCEL, method="PATCH")
    assert r.status_code == 400
    r = preflight(make_client(), VERCEL, headers="authorization")
    assert r.status_code == 400


def test_cors_headers_on_real_responses_and_admin_key_header_allowed(client):
    r = make_client().get("/api/devices", headers={"Origin": VERCEL})
    assert r.headers["access-control-allow-origin"] == VERCEL
    assert preflight(make_client(), VERCEL, "GET", "x-admin-key", "/api/admin/datasets").status_code == 200


def test_wildcard_origin_is_refused_and_trailing_slashes_are_cleaned():
    with pytest.raises(Exception, match="explicit origins"):
        Settings(_env_file=None, database_url="sqlite://", cors_origins="*")
    assert Settings(_env_file=None, database_url="sqlite://", cors_origins=" https://a.app/ , http://localhost:5173/ ").cors_list == ["https://a.app", "http://localhost:5173"]
    assert VERCEL in Settings(_env_file=None, database_url="sqlite://").cors_list          # production origin is built in


def test_origin_regex_for_preview_deployments_is_anchored():
    s = Settings(_env_file=None, database_url="sqlite://", cors_origin_regex=r"^https://smart-device-forcast-1-[a-z0-9]+-myteam\.vercel\.app$")
    assert re.match(s.cors_origin_regex, "https://smart-device-forcast-1-abc123-myteam.vercel.app")
    assert not re.match(s.cors_origin_regex, "https://smart-device-forcast-1-abc123-myteam.vercel.app.evil.com")


# ------------------------------------------------------------------- database URL and proxy
@pytest.mark.parametrize("raw,expected", [
    ("postgres://u:p@h/d", "postgresql+psycopg2://u:p@h/d"), ("postgresql://u:p@h/d", "postgresql+psycopg2://u:p@h/d"),
    ("postgresql+psycopg2://u:p@h/d", "postgresql+psycopg2://u:p@h/d"), ("sqlite:///./dev.db", "sqlite:///./dev.db")])
def test_database_url_is_normalised_for_render(raw, expected):
    assert normalize_database_url(raw) == expected


def _req(xff=None):
    headers = [(b"x-forwarded-for", xff.encode())] if xff else []
    return Request({"type": "http", "headers": headers, "client": ("10.0.0.9", 1), "method": "GET", "path": "/", "query_string": b""})


def test_rate_limit_uses_real_client_ip_only_behind_a_trusted_proxy(monkeypatch):
    monkeypatch.setattr(settings, "trust_proxy", False)
    assert client_ip(_req("6.6.6.6")) == "10.0.0.9"
    monkeypatch.setattr(settings, "trust_proxy", True)
    assert client_ip(_req("1.2.3.4, 203.0.113.7")) == "203.0.113.7" and client_ip(_req()) == "10.0.0.9"
