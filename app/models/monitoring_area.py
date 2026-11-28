from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.db.spatial import geojson_column


class MonitoringAreaDB(Base):
    __tablename__ = "monitoring_areas"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    crs: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    geometry: Mapped[dict] = mapped_column(
        geojson_column(),
        nullable=False,
    )