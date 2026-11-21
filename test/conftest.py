
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.monitoring_area import MonitoringAreaDB
from app.db.database import (
    Base,
    get_db,
    enable_sqlite_foreign_keys,
)

# Register all database models.
import app.models.detection
import app.models.infrastructure_asset
import app.models.satellite_image

from app.main import app


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    """Create a separate database for each test."""

    db_path = tmp_path / "test_api.sqlite3"

    test_engine = create_engine(
        f"sqlite:///{db_path.as_posix()}"
    )

    # Enable SQLite foreign-key enforcement.
    enable_sqlite_foreign_keys(test_engine)

    # Create all database tables.
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        with Session(test_engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    yield test_engine

    app.dependency_overrides.pop(get_db, None)

    test_engine.dispose()

def sample_monitoring_area_geometry():
    return {
        "type": "Polygon",
        "coordinates": [[
            [31.0, 30.0],
            [31.1, 30.0],
            [31.1, 30.1],
            [31.0, 30.1],
            [31.0, 30.0],
        ]],
    }


@pytest.fixture
def monitoring_area(isolated_database):
    with Session(isolated_database) as db:
        area = MonitoringAreaDB(
            name="Test Monitoring Area",
            crs="EPSG:4326",
            geometry=sample_monitoring_area_geometry(),
        )

        db.add(area)
        db.commit()
        db.refresh(area)

        return area.id


@pytest.fixture
def two_monitoring_areas(isolated_database, monitoring_area):
    with Session(isolated_database) as db:
        second_area = MonitoringAreaDB(
            name="Second Test Monitoring Area",
            crs="EPSG:4326",
            geometry=sample_monitoring_area_geometry(),
        )

        db.add(second_area)
        db.commit()
        db.refresh(second_area)

        return monitoring_area, second_area.id
