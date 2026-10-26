from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (JSON, Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


CATEGORIES = ("Laptop", "Smartphone")
STATUSES = ("Active", "Discontinued", "Upcoming")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    token_version: Mapped[int] = mapped_column(Integer, default=0)  # bumped on logout -> revokes tokens
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("role in ('user','admin')", name="ck_users_role"),)


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)  # e.g. LP001 (CSV device_id)
    name: Mapped[str] = mapped_column(String(160), index=True)
    brand: Mapped[str] = mapped_column(String(80), index=True)
    category: Mapped[str] = mapped_column(String(12), index=True)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    launch_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(14), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    specs: Mapped[list[DeviceSpec]] = relationship(back_populates="device", cascade="all, delete-orphan",
                                                   passive_deletes=True, lazy="selectin")
    __table_args__ = (
        CheckConstraint("category in ('Laptop','Smartphone')", name="ck_devices_category"),
        CheckConstraint("launch_price > 0", name="ck_devices_launch_price"),
    )


class DeviceSpec(Base):
    __tablename__ = "device_specs"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(60))
    value: Mapped[str] = mapped_column(String(255))
    device: Mapped[Device] = relationship(back_populates="specs")
    __table_args__ = (UniqueConstraint("device_id", "key", name="uq_spec_device_key"),)


class Dataset(Base):
    __tablename__ = "datasets"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    checksum: Mapped[str] = mapped_column(String(64))
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    rows_total: Mapped[int] = mapped_column(Integer, default=0)
    rows_valid: Mapped[int] = mapped_column(Integer, default=0)
    rows_invalid: Mapped[int] = mapped_column(Integer, default=0)
    rows_duplicate: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="processed")
    report: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    price: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3))
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (
        UniqueConstraint("device_id", "date", "source", name="uq_price_device_date_source"),
        CheckConstraint("price > 0", name="ck_price_positive"),
        Index("ix_price_device_date", "device_id", "date"),
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(12), index=True)
    model_type: Mapped[str] = mapped_column(String(60))
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    dataset_version: Mapped[str] = mapped_column(String(40))
    n_observations: Mapped[int] = mapped_column(Integer)
    metrics: Mapped[dict] = mapped_column(JSON)
    candidates: Mapped[list] = mapped_column(JSON)
    feature_set: Mapped[dict] = mapped_column(JSON)
    artifact_path: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    trained_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[str | None] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    model_version_id: Mapped[int | None] = mapped_column(ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    kind: Mapped[str] = mapped_column(String(10))  # predict | forecast
    # snapshots keep history readable even if the device/model is later deleted
    device_name: Mapped[str] = mapped_column(String(160))
    brand: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(12))
    currency: Mapped[str] = mapped_column(String(3))
    current_price: Mapped[float] = mapped_column(Float)
    as_of: Mapped[date] = mapped_column(Date)
    horizons: Mapped[list] = mapped_column(JSON)
    results: Mapped[list] = mapped_column(JSON)
    path: Mapped[list] = mapped_column(JSON)
    history: Mapped[list] = mapped_column(JSON)
    stats: Mapped[dict] = mapped_column(JSON)
    model_info: Mapped[dict] = mapped_column(JSON)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    device_id: Mapped[str | None] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    prediction_id: Mapped[int | None] = mapped_column(ForeignKey("predictions.id", ondelete="SET NULL"), nullable=True)
    event: Mapped[str] = mapped_column(String(30))  # predict | forecast | train
    status: Mapped[str] = mapped_column(String(10))  # ok | error
    message: Mapped[str] = mapped_column(Text, default="")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
