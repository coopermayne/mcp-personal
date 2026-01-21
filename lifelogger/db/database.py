"""Database connection and session management."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def get_database_url() -> str:
    """Get database URL from environment variable."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return url


def get_async_database_url() -> str:
    """Get async database URL from environment variable."""
    url = os.environ.get("DATABASE_URL_ASYNC")
    if url:
        return url
    # Convert sync URL to async URL
    sync_url = get_database_url()
    if sync_url.startswith("postgresql://"):
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return sync_url


# Sync engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the sync database engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url(), pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


def get_session() -> Session:
    """Create a new database session."""
    SessionLocal = get_session_factory()
    return SessionLocal()


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database (create all tables)."""
    Base.metadata.create_all(bind=get_engine())


# FastAPI dependency
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()
