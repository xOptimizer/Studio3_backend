"""SQLAlchemy 2.0 engine, session factory, and declarative Base."""
import os
from typing import Generator
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session


def _sanitize_database_url(url: str) -> str:
    """Remove query params that psycopg2 does not accept (e.g. pgbouncer=true from Supabase)."""
    parsed = urlparse(url)
    if not parsed.query:
        return url
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("pgbouncer", None)
    if not params:
        return urlunparse(parsed._replace(query=""))
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


_raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/flask_app_dev",
)
DATABASE_URL = _sanitize_database_url(_raw_url)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session; caller must close/commit/rollback."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Run SELECT 1 to verify DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
