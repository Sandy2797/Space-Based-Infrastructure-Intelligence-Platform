from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SatelliteImageDB(Base):
    __tablename__ = "satellite_images"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    monitoring_area_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_areas.id",
            name="fk_satellite_images_monitoring_area_id_monitoring_areas",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    file_reference: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    crs: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    band_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
