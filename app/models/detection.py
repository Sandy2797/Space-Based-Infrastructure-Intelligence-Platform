
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.db.spatial import geojson_column


class DetectionDB(Base):
    __tablename__ = "detections"

    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_detections_confidence",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    before_image_id: Mapped[int] = mapped_column(
        ForeignKey("satellite_images.id"),
        nullable=False,
        index=True,
    )

    after_image_id: Mapped[int] = mapped_column(
        ForeignKey("satellite_images.id"),
        nullable=False,
        index=True,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    component_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    geometry: Mapped[dict] = mapped_column(
        geojson_column(),
        nullable=False,
    )

    origin_category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    change_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    threshold: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    pixel_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    area_m2: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    evidence_quality: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    quality_flags: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    mask_reference: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    model_version: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
