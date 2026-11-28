import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

load_dotenv()

if os.getenv("DB_PASSWORD"):
    from sqlalchemy.engine import URL

    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER", "space_user"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5433")),
        database=os.getenv("DB_NAME", "space_infra"),
    )
else:
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
