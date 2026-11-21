from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.db.spatial import geojson_column


class InfrastructureAssetDB(Base):
    __tablename__ = "infrastructure_assets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    monitoring_area_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_areas.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    asset_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    location: Mapped[dict] = mapped_column(
        geojson_column(),
        nullable=False,
    )