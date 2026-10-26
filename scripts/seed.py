"""Usage:
  python -m scripts.seed --sample            fresh install: schema + sample catalogue (only if catalogue is empty)
  python -m scripts.seed --sync-catalog      EXISTING database: add any missing catalogue devices / price rows (idempotent)
  python -m scripts.seed --retire-legacy-demo   remove the old fictional demo devices (Acme, Zenith, Nova, Orbit, Kestrel)
Options can be combined and are safe to run repeatedly. Nothing here deletes users, predictions or your own data.
"""
import argparse

from backend.app.db import Base, SessionLocal, engine
from backend.app.services import seed

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="load the sample catalogue if the catalogue is empty")
    ap.add_argument("--force", action="store_true", help="with --sample: load even if devices already exist")
    ap.add_argument("--sync-catalog", action="store_true", help="add missing sample devices + price rows (idempotent)")
    ap.add_argument("--retire-legacy-demo", action="store_true", help="remove the old fictional demo devices")
    a = ap.parse_args()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if a.sample:
            print(seed.seed_sample(db, force=a.force))
        if a.retire_legacy_demo:
            print(seed.retire_legacy_demo(db))
        if a.sync_catalog:
            print(seed.sync_catalog(db))
