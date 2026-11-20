import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base, get_db
from app.main import app
from app.models.satellite_image import SatelliteImageDB


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    """Create a separate database for each test."""

    db_path = tmp_path / "test_api.sqlite3"

    test_engine = create_engine(
        f"sqlite:///{db_path.as_posix()}"
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        with Session(test_engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.pop(get_db, None)

    test_engine.dispose()