from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.db.spatial import geojson_column


class DetectionDB(Base):
    __tablename__ = "detections"

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
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

    geometry: Mapped[dict] = mapped_column(
        geojson_column("POINT"),
        nullable=False,
    )

    origin_category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )