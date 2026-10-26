from datetime import date

import pytest

from backend.app.services.csv_validation import CSVFormatError, validate_price_csv

DEVS = {"LP001": {"name": "Test Laptop", "category": "Laptop", "currency": "INR"}}
HEAD = "device_id,device_name,category,date,price,source,currency\n"


def v(rows: str, existing=None):
    return validate_price_csv((HEAD + rows).encode(), DEVS, existing, today=date(2026, 10, 1))


def test_valid_rows():
    r = v("LP001,Test Laptop,Laptop,2026-01-01,129999,shop,INR\nLP001,Test Laptop,Laptop,2026-02-01,\"1,27,999\",shop,INR\n".replace('"1,27,999"', "127999"))
    assert len(r.valid_rows) == 2 and r.error_count == 0


def test_detects_each_problem():
    r = v("\n".join([
        "LP001,Test Laptop,Laptop,2026-13-45,100,s,INR",        # invalid date
        "LP001,Test Laptop,Laptop,2026-01-01,abc,s,INR",        # invalid price
        "LP001,Test Laptop,Laptop,2026-01-02,-5,s,INR",         # negative price
        "LP001,Test Laptop,Laptop,2026-01-03,,s,INR",           # missing price
        "XX999,Ghost,Laptop,2026-01-01,100,s,INR",              # invalid device
        "LP001,Test Laptop,Laptop,2027-01-01,100,s,INR",        # future date
        "LP001,Wrong Name,Laptop,2026-01-04,100,s,INR",         # name mismatch
        "LP001,Test Laptop,Smartphone,2026-01-05,100,s,INR",    # category mismatch
        "LP001,Test Laptop,Laptop,2026-01-06,100,s,USD",        # currency mismatch
        "LP001,Test Laptop,Laptop,2026-02-01,100,s,INR",        # ok
        "LP001,Test Laptop,Laptop,2026-02-01,101,s,INR",        # duplicate in file
        "LP001,Test Laptop,Laptop,2026-03-01,100,s,INR",        # duplicate of existing
    ]), existing={("LP001", date(2026, 3, 1), "s")})
    codes = {e["code"] for e in r.errors}
    assert {"invalid_date", "invalid_price", "missing_value", "invalid_device_id", "future_date", "device_name_mismatch",
            "category_mismatch", "currency_mismatch", "duplicate_in_file", "duplicate_existing"} <= codes
    assert len(r.valid_rows) == 1 and r.duplicates_in_file == 1 and r.duplicates_existing == 1
    assert r.invalid_device_ids == {"XX999"} and r.missing_values == 1
    assert all(e["row"] >= 2 for e in r.errors)


def test_file_level_errors():
    with pytest.raises(CSVFormatError, match="Missing required column"):
        validate_price_csv(b"device_id,price\nLP001,1\n", DEVS)
    with pytest.raises(CSVFormatError, match="empty"):
        validate_price_csv(b"  \n", DEVS)
    with pytest.raises(CSVFormatError, match="no data rows"):
        validate_price_csv(HEAD.encode(), DEVS)
    with pytest.raises(CSVFormatError, match="UTF-8"):
        validate_price_csv(b"\xff\xfeabc,def\n1,2\n", DEVS)


# ---- API level ---------------------------------------------------------------------------
def _csv(rows):
    return {"file": ("prices.csv", (HEAD + rows).encode(), "text/csv")}


def test_upload_stores_valid_rows_and_reports_errors(admin):
    from .conftest import add_device
    add_device(months=1, did="LP001", name="Test Laptop X")
    from backend.app.db import SessionLocal
    from backend.app.models import PriceHistory
    rows = ("LP001,Test Laptop X,Laptop,2026-01-01,90000,shop,INR\n"
            "LP001,Test Laptop X,Laptop,bad-date,90000,shop,INR\n"
            "NOPE,Ghost,Laptop,2026-01-01,5,shop,INR\n")
    r = admin.post("/api/admin/dataset/upload", files=_csv(rows))
    assert r.status_code == 201, r.text
    j = r.json()
    assert j["dataset"]["rows_valid"] == 1 and j["report"]["error_count"] == 2 and j["report"]["invalid_device_ids"] == ["NOPE"]
    with SessionLocal() as db:
        assert db.query(PriceHistory).filter_by(source="shop").count() == 1
    again = admin.post("/api/admin/dataset/upload", files=_csv(rows)).json()
    assert again["report"]["duplicates_existing"] == 1 and again["dataset"]["rows_valid"] == 0
    assert len(admin.get("/api/admin/datasets").json()) == 2


def test_validate_endpoint_stores_nothing(admin):
    from .conftest import add_device
    from backend.app.db import SessionLocal
    from backend.app.models import PriceHistory
    add_device(months=1)
    r = admin.post("/api/admin/dataset/validate", files=_csv("LP001,Test Laptop X,Laptop,2026-01-01,90000,v,INR\n"))
    assert r.status_code == 200 and r.json()["valid_rows"] == 1
    with SessionLocal() as db:
        assert db.query(PriceHistory).filter_by(source="v").count() == 0


def test_upload_rejects_bad_files(admin, monkeypatch):
    r = admin.post("/api/admin/dataset/upload", files={"file": ("x.exe", b"MZ...", "application/octet-stream")})
    assert r.status_code == 415
    r = admin.post("/api/admin/dataset/upload", files={"file": ("x.csv", b"", "text/csv")})
    assert r.status_code == 422
    r = admin.post("/api/admin/dataset/upload", files={"file": ("x.csv", b"a,b\n1,2\n", "text/csv")})
    assert r.status_code == 422 and r.json()["code"] == "invalid_csv" and "Missing required column" in r.json()["detail"]
    from backend.app.routers import admin as admin_router
    monkeypatch.setattr(admin_router.settings, "max_upload_mb", 0)
    big = admin.post("/api/admin/dataset/upload", files={"file": ("x.csv", b"a" * 10, "text/csv")})
    assert big.status_code == 413


def test_upload_requires_admin_key(user):
    r = user.post("/api/admin/dataset/upload", files=_csv("x"))   # a normal visitor has no admin key
    assert r.status_code == 401 and r.json()["code"] == "admin_key_required"


def test_export_processed_csv(admin):
    from .conftest import add_device
    add_device(months=3)
    r = admin.get("/api/admin/dataset/export")
    assert r.status_code == 200 and len(r.text.strip().splitlines()) == 4
