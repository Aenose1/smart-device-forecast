import os
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
TEMP_DIR = Path(tempfile.gettempdir())
TEMP_DB_PATH = TEMP_DIR / "smart_device_forecast.db"
TEMP_DB_URL = f"sqlite:///{TEMP_DB_PATH.as_posix()}"

# Origins allowed to call the API from a browser.
DEFAULT_CORS_ORIGINS = (
    "https://smart-device-forcast-1.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"
)


def normalize_database_url(url: str) -> str:
    """Render/Heroku/Vercel URLs -> driver URL SQLAlchemy 2 understands."""
    url = (url or "").strip()
    if not url:
        url = TEMP_DB_URL if IS_VERCEL else "sqlite:///./dev.db"

    if IS_VERCEL and url.startswith("sqlite"):
        try:
            if not TEMP_DB_PATH.exists() and (ROOT / "dev.db").exists():
                shutil.copy2(ROOT / "dev.db", TEMP_DB_PATH)
            url = f"sqlite:///{TEMP_DB_PATH.as_posix()}"
        except Exception:
            pass

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


class Settings(BaseSettings):
    """Configuration comes from environment variables (.env locally, Vercel/Render in production)."""

    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    database_url: str = TEMP_DB_URL if IS_VERCEL else "sqlite:///./dev.db"
    environment: str = "production" if IS_VERCEL else "development"
    cors_origins: str = DEFAULT_CORS_ORIGINS
    cors_origin_regex: str = ""
    trust_proxy: bool = IS_VERCEL or bool(os.environ.get("RENDER"))
    trusted_proxy_hops: int = 1
    admin_api_key: str = ""
    allow_open_admin: bool = False
    max_upload_mb: int = 10
    rate_limit_enabled: bool = not IS_VERCEL
    max_forecast_years: int = 5
    default_forecast_years: int = 3
    models_dir: str = (TEMP_DIR / "sdf_models").as_posix() if IS_VERCEL else "models"
    uploads_dir: str = (TEMP_DIR / "sdf_uploads").as_posix() if IS_VERCEL else "data/uploads"
    sample_dir: str = "data/sample"
    seed_sample_data: bool = False
    serve_frontend: bool = True
    frontend_dist: str = "frontend/dist"

    @field_validator("database_url")
    @classmethod
    def _db_url(cls, v: str) -> str:
        return normalize_database_url(v)

    @field_validator("cors_origins")
    @classmethod
    def _origins(cls, v: str) -> str:
        items = [o.strip().rstrip("/") for o in v.split(",") if o.strip()]
        if "*" in items:
            raise ValueError("CORS_ORIGINS must list explicit origins, not '*'")
        return ",".join(items)

    @field_validator("admin_api_key")
    @classmethod
    def _admin_key(cls, v: str) -> str:
        v = v.strip()
        if v and len(v) < 16:
            raise ValueError("ADMIN_API_KEY must be at least 16 characters (use a long random value)")
        return v

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production" or bool(os.environ.get("RENDER")) or IS_VERCEL

    @property
    def admin_mode(self) -> str:
        """'key' (header required), 'open' (demo only, never in production) or 'disabled'."""
        if self.admin_api_key:
            return "key"
        if self.allow_open_admin and not self.is_production:
            return "open"
        return "disabled"

    def path(self, p: str) -> Path:
        q = Path(p)
        return q if q.is_absolute() else ROOT / q


@lru_cache
def get_settings() -> Settings:
    return Settings()
