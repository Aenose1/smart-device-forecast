"""Validation of historical price CSV files (no database access: pure & unit-testable)."""
from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass, field
from datetime import date, datetime

REQUIRED_COLUMNS = ["device_id", "device_name", "category", "date", "price", "source", "currency"]
MAX_REPORTED_ERRORS = 500


class CSVFormatError(Exception):
    """File-level problem (not decodable, wrong columns, empty)."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message, self.details = message, details or {}


@dataclass
class ValidationReport:
    total_rows: int = 0
    valid_rows: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    error_count: int = 0
    duplicates_in_file: int = 0
    duplicates_existing: int = 0
    missing_values: int = 0
    invalid_device_ids: set[str] = field(default_factory=set)

    def add_error(self, row: int, code: str, message: str, column: str | None = None) -> None:
        self.error_count += 1
        if len(self.errors) < MAX_REPORTED_ERRORS:
            self.errors.append({"row": row, "column": column, "code": code, "message": message})

    def summary(self) -> dict:
        invalid_rows = len({e["row"] for e in self.errors}) if self.error_count <= MAX_REPORTED_ERRORS else None
        return {
            "total_rows": self.total_rows,
            "valid_rows": len(self.valid_rows),
            "invalid_rows": self.total_rows - len(self.valid_rows) - self.duplicates_in_file - self.duplicates_existing,
            "duplicates_in_file": self.duplicates_in_file,
            "duplicates_existing": self.duplicates_existing,
            "missing_values": self.missing_values,
            "invalid_device_ids": sorted(self.invalid_device_ids)[:100],
            "error_count": self.error_count,
            "errors": self.errors,
            "errors_truncated": self.error_count > len(self.errors),
            "_invalid_row_estimate": invalid_rows,
        }


def parse_date(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def validate_price_csv(content: bytes, devices: dict[str, dict], existing_keys: set[tuple[str, date, str]] | None = None,
                       today: date | None = None) -> ValidationReport:
    """devices: {device_id: {"name","category","currency"}}; existing_keys: {(device_id, date, source)}."""
    existing_keys = existing_keys or set()
    today = today or date.today()
    if b"\x00" in content[:4096]:
        raise CSVFormatError("The file looks binary, not like a CSV text file.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise CSVFormatError("The file is not valid UTF-8 text.") from None
    if not text.strip():
        raise CSVFormatError("The file is empty.")
    reader = csv.DictReader(io.StringIO(text))
    header = [h.strip().lower() for h in (reader.fieldnames or [])]
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise CSVFormatError(f"Missing required column(s): {', '.join(missing)}.",
                             {"required": REQUIRED_COLUMNS, "found": header})
    reader.fieldnames = header

    rep = ValidationReport()
    seen: set[tuple[str, date, str]] = set()
    for i, raw in enumerate(reader, start=2):  # row 1 is the header
        rep.total_rows += 1
        row = {k: (v or "").strip() for k, v in raw.items() if k in REQUIRED_COLUMNS}
        before = rep.error_count
        blanks = [c for c in REQUIRED_COLUMNS if not row.get(c)]
        for c in blanks:
            rep.add_error(i, "missing_value", f"'{c}' is empty.", c)
        rep.missing_values += len(blanks)

        dev = devices.get(row.get("device_id", ""))
        if row.get("device_id") and dev is None:
            rep.invalid_device_ids.add(row["device_id"])
            rep.add_error(i, "invalid_device_id", f"Device ID '{row['device_id']}' does not exist.", "device_id")
        if dev:
            if row["device_name"] and row["device_name"].lower() != dev["name"].lower():
                rep.add_error(i, "device_name_mismatch",
                              f"Name '{row['device_name']}' does not match device {row['device_id']} ('{dev['name']}').", "device_name")
            if row["category"] and row["category"].lower() != dev["category"].lower():
                rep.add_error(i, "category_mismatch", f"Category '{row['category']}' does not match '{dev['category']}'.", "category")
            cur = row["currency"].upper()
            if cur and cur != dev["currency"]:
                rep.add_error(i, "currency_mismatch", f"Currency '{cur}' does not match the device currency '{dev['currency']}'.", "currency")

        d = None
        if row.get("date"):
            try:
                d = parse_date(row["date"])
                if d > today:
                    rep.add_error(i, "future_date", f"Date {row['date']} is in the future.", "date")
                    d = None
            except ValueError:
                rep.add_error(i, "invalid_date", f"'{row['date']}' is not a valid date (use YYYY-MM-DD).", "date")
        price = None
        if row.get("price"):
            try:
                price = float(row["price"].replace(",", ""))
                if not math.isfinite(price) or price <= 0:
                    raise ValueError
            except ValueError:
                price = None
                rep.add_error(i, "invalid_price", f"'{row['price']}' is not a positive number.", "price")
        if len(row.get("source", "")) > 120:
            rep.add_error(i, "source_too_long", "'source' must be at most 120 characters.", "source")

        if rep.error_count != before or d is None or price is None or dev is None:
            continue
        key = (row["device_id"], d, row["source"])
        if key in seen:
            rep.duplicates_in_file += 1
            rep.add_error(i, "duplicate_in_file", f"Duplicate of an earlier row (device, date, source): {key[0]}, {d}, {key[2]}.")
            continue
        seen.add(key)
        if key in existing_keys:
            rep.duplicates_existing += 1
            rep.add_error(i, "duplicate_existing", f"Record already stored (device, date, source): {key[0]}, {d}, {key[2]}.")
            continue
        rep.valid_rows.append({"device_id": row["device_id"], "date": d, "price": price,
                               "source": row["source"], "currency": row["currency"].upper()})
    if rep.total_rows == 0:
        raise CSVFormatError("The file has a header but no data rows.")
    return rep
