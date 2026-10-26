import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, SessionLocal, engine, get_db
from .errors import install_handlers
from .models import Device
from .routers import admin, dashboard, devices, predictions, public
from .services import seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
settings = get_settings()


def log_startup_diagnostics() -> None:
    """Non-secret summary of the settings that matter in production; visible in the Render logs."""
    log = logging.getLogger("app.startup")
    dialect = engine.dialect.name
    log.info("Config: db=%s production=%s cors_origins=%s cors_regex=%s admin=%s trust_proxy=%s", dialect, settings.is_production,
             settings.cors_list or "-", "set" if settings.cors_origin_regex else "-", settings.admin_mode, settings.trust_proxy)
    if dialect == "sqlite" and os.environ.get("RENDER"):
        log.warning("DATABASE_URL points to SQLite on Render. Render's filesystem is ephemeral: every redeploy, restart and "
                    "idle spin-down DELETES the database (forecast history, uploaded datasets). Use a PostgreSQL DATABASE_URL.")
    if settings.is_production and settings.admin_mode == "disabled":
        log.info("Administration is disabled (ADMIN_API_KEY is not set). Public features are unaffected.")
    if settings.allow_open_admin and settings.is_production:
        log.warning("ALLOW_OPEN_ADMIN is ignored in production; set ADMIN_API_KEY to use the admin pages.")
    if settings.allow_open_admin and not settings.is_production and not settings.admin_api_key:
        log.warning("DEMO MODE: administration is OPEN without a key (ALLOW_OPEN_ADMIN=true). Never use this on a public server.")
    if os.environ.get("RENDER") and not settings.trust_proxy:
        log.warning("TRUST_PROXY is false on Render: all visitors share one rate-limit bucket. Set TRUST_PROXY=true.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    log_startup_diagnostics()
    Base.metadata.create_all(engine)
    try:
        settings.path(settings.models_dir).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    try:
        settings.path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    with SessionLocal() as db:
        if settings.seed_sample_data:
            logging.getLogger("app").info("Sample seed: %s", seed.seed_sample(db))
    yield


app = FastAPI(title="Smart Device Price Prediction & 3-Year Forecasting System", version="1.0.0", lifespan=lifespan,
              docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)
install_handlers(app)
# CORS: only the listed origins (production Vercel site + local dev by default), only the methods and headers the app uses.
# No cookies or credentials are used anywhere, so allow_credentials stays False.
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_origin_regex=settings.cors_origin_regex or None,
                   allow_credentials=False, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                   allow_headers=["Content-Type", "Accept", "X-Visitor-Id", "X-Admin-Key"],
                   expose_headers=["Content-Disposition"], max_age=600)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    if request.url.path.startswith("/api/") and not request.url.path.startswith("/api/docs"):
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp


api = APIRouter(prefix="/api")


@api.get("/health", tags=["meta"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


for r in (public.router, devices.router, predictions.router, dashboard.router, admin.router):
    api.include_router(r)
app.include_router(api)

# --- serve the built React app (single-container deployment) -----------------------------------
_dist = settings.path(settings.frontend_dist)
if settings.serve_frontend and (_dist / "index.html").exists():
    if (_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Resource not found.", "code": "http_error"}, status_code=404)
        f = (_dist / full_path).resolve()
        if full_path and _dist.resolve() in f.parents and f.is_file():
            return FileResponse(f)
        return FileResponse(_dist / "index.html")
