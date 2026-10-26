import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("VERCEL", "1")
os.environ.setdefault("SEED_SAMPLE_DATA", "true")

from backend.app.main import app  # noqa: F401
