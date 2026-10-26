import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ID_RE = re.compile(r"^[A-Za-z0-9_-]{2,32}$")
Category = Literal["Laptop", "Smartphone"]
Status = Literal["Active", "Discontinued", "Upcoming"]


class DeviceIn(BaseModel):
    device_id: str
    name: str = Field(min_length=1, max_length=160)
    brand: str = Field(min_length=1, max_length=80)
    category: Category
    release_date: date | None = None
    launch_price: float = Field(gt=0, lt=1e9)
    current_price: float | None = Field(default=None, gt=0, lt=1e9)
    currency: str = "INR"
    status: Status = "Active"
    specs: dict[str, str] = Field(default_factory=dict)

    @field_validator("device_id")
    @classmethod
    def _id(cls, v: str) -> str:
        v = v.strip()
        if not ID_RE.match(v):
            raise ValueError("Device ID must be 2-32 characters: letters, digits, '-' or '_'")
        return v

    @field_validator("currency")
    @classmethod
    def _cur(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", v):
            raise ValueError("Currency must be a 3-letter code such as INR")
        return v

    @field_validator("specs")
    @classmethod
    def _specs(cls, v: dict[str, str]) -> dict[str, str]:
        if len(v) > 40:
            raise ValueError("At most 40 specifications are allowed")
        out = {}
        for k, val in v.items():
            k, val = str(k).strip(), str(val).strip()
            if not k or len(k) > 60 or len(val) > 255:
                raise ValueError("Spec names must be 1-60 characters and values at most 255")
            if val:
                out[k] = val
        return out


class ForecastIn(BaseModel):
    device_id: str
    years: int = Field(default=3, ge=1, le=10)  # horizon; capped by MAX_FORECAST_YEARS server-side


class PredictIn(BaseModel):
    device_id: str
    months: int = Field(ge=1, le=120)


class TrainIn(BaseModel):
    device_id: str | None = None
    category: Category | None = None


def specs_to_dict(device) -> dict[str, str]:
    return {s.key: s.value for s in sorted(device.specs, key=lambda s: s.key.lower())}
