
import os
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./space_infra_dev.sqlite3",
)

engine = create_engine(DATABASE_URL)


def enable_sqlite_foreign_keys(target_engine: Engine) -> None:
    if target_engine.dialect.name != "sqlite":
        return

    @event.listens_for(target_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Enable foreign-key enforcement for the application database.
enable_sqlite_foreign_keys(engine)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db
