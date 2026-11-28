from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.satellite_image import SatelliteImageDB


def test_satellite_image_persists_to_database(tmp_path):
    db_path = tmp_path / "test_images.sqlite3"

    test_engine = create_engine(
        f"sqlite:///{db_path.as_posix()}"
    )

    Base.metadata.create_all(bind=test_engine)

    image = SatelliteImageDB(
        monitoring_area_id=1,
        provider="Test Provider",
        file_reference="satellite_before.tif",
        acquired_at=datetime(
            2026, 11, 20, 10, 0,
            tzinfo=timezone.utc,
        ),
        crs="EPSG:4326",
        width=1024,
        height=1024,
        band_count=3,
    )

    with Session(test_engine) as session:
        session.add(image)
        session.commit()

    # A new session should still find the saved record.
    with Session(test_engine) as session:
        saved_image = session.scalar(
            select(SatelliteImageDB).where(
                SatelliteImageDB.file_reference
                == "satellite_before.tif"
            )
        )

        assert saved_image is not None
        assert saved_image.id == 1
        assert saved_image.monitoring_area_id == 1
        assert saved_image.width == 1024
        assert saved_image.crs == "EPSG:4326"

    test_engine.dispose()