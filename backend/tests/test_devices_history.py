from .conftest import add_device, make_client


def test_search_filters(user):
    add_device("LP001", "Acme Blade 16", "Laptop", brand="Acme", launch=120000)
    add_device("SP001", "Nova Phone Pro", "Smartphone", brand="Nova", launch=60000)
    add_device("LP002", "Zenith Air 14", "Laptop", brand="Zenith", launch=80000)
    j = lambda **p: user.get("/api/devices/search", params=p).json()  # noqa: E731
    assert j()["total"] == 3
    assert [d["id"] for d in j(q="blade")["items"]] == ["LP001"]
    assert {d["id"] for d in j(q="nova")["items"]} == {"SP001"}          # brand match
    assert {d["id"] for d in j(category="Laptop")["items"]} == {"LP001", "LP002"}
    assert {d["id"] for d in j(brand="zenith")["items"]} == {"LP002"}
    assert all(d["latest_price"] for d in j()["items"])
    assert j(q="%")["total"] == 0                                         # wildcard characters are escaped
    assert user.get("/api/devices/search", params={"min_price": 10, "max_price": 5}).status_code == 422


def test_price_range_uses_latest_price(user):
    add_device("LP001", "A", launch=100000, decay=0.05)   # latest ~ 30k
    add_device("LP002", "B", launch=100000, decay=0.001)  # latest ~ 97k
    ids = lambda **p: {d["id"] for d in user.get("/api/devices", params=p).json()["items"]}  # noqa: E731
    assert ids(max_price=50000) == {"LP001"}
    assert ids(min_price=50000) == {"LP002"}


def test_sql_injection_attempt_is_inert(user):
    add_device()
    r = user.get("/api/devices/search", params={"q": "'; DROP TABLE devices; --"})
    assert r.status_code == 200 and r.json()["total"] == 0
    assert user.get("/api/devices/search").json()["total"] == 1


def test_price_history_stats(user):
    add_device(months=12, decay=0.002)  # flat-ish series so both rises and drops occur
    h = user.get("/api/devices/LP001/history").json()
    s = h["stats"]
    assert s["records"] == 12 == len(h["history"])
    assert s["min_price"] <= s["avg_price"] <= s["max_price"] and s["pct_change"] < 0
    assert s["highest_drop"]["amount"] < 0 and s["highest_increase"]["amount"] > 0
    assert s["current_price"] == h["history"][-1]["price"]


def test_history_missing_device_and_empty_history(user):
    assert user.get("/api/devices/NOPE/history").status_code == 404
    from backend.app.db import SessionLocal
    from backend.app.models import Device
    with SessionLocal() as db:
        db.add(Device(id="EMPTY1", name="Empty", brand="B", category="Laptop", launch_price=1000, currency="INR"))
        db.commit()
    h = user.get("/api/devices/EMPTY1/history").json()
    assert h["stats"] is None and h["history"] == []


def test_history_csv_download(user):
    add_device(months=6)
    r = user.get("/api/devices/LP001/history", params={"format": "csv"})
    assert r.status_code == 200 and r.text.splitlines()[0] == "device_id,device_name,category,date,price,source,currency"
    assert len(r.text.strip().splitlines()) == 7


def test_public_overview_needs_no_login_and_exposes_only_catalogue_data(client):
    add_device("LP900", "Test Laptop Q", "Laptop", brand="Acme")
    add_device("SP900", "Test Phone Q", "Smartphone", brand="Zeta")
    r = make_client().get("/api/public/overview")
    assert r.status_code == 200
    body = r.json()
    assert [b["brand"] for b in body["brands"]["Laptop"]] == ["Acme"] and [b["brand"] for b in body["brands"]["Smartphone"]] == ["Zeta"]
    assert {d["id"] for d in body["featured"]} == {"LP900", "SP900"} and body["total_devices"] == 2
    assert "email" not in r.text and "password" not in r.text
    # the whole catalogue is public too (no login exists any more)
    assert make_client().get("/api/devices").status_code == 200
