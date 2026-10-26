"""Writes database/schema.sql (PostgreSQL DDL) from the SQLAlchemy models."""
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from backend.app.db import Base
from backend.app import models  # noqa: F401

out = []
for t in Base.metadata.sorted_tables:
    out.append(str(CreateTable(t).compile(dialect=postgresql.dialect())).strip() + ";")
    out += [str(CreateIndex(i).compile(dialect=postgresql.dialect())).strip() + ";" for i in t.indexes]
Path(__file__).resolve().parents[1].joinpath("database", "schema.sql").write_text("\n\n".join(out) + "\n")
print("database/schema.sql written")
