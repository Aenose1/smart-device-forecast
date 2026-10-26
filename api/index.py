import os
import sys
from pathlib import Path

# Ensure the project root is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Mark environment as Vercel and ensure sample data is seeded on cold start
os.environ.setdefault("VERCEL", "1")
os.environ.setdefault("SEED_SAMPLE_DATA", "true")

from backend.app.main import app  # noqa: E402
