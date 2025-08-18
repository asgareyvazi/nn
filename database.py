
# =========================================
# file: nikan_drill_master/database.py
# =========================================
from __future__ import annotations
from contextlib import contextmanager
from typing import Iterator, Callable, Type
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

# مهم: فعال‌سازی FK در SQLite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-redef]
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def init_engine_and_session(url: str) -> tuple[Engine, Callable[[], Session]]:
    engine = create_engine(url, echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    return engine, SessionLocal

@contextmanager
def session_scope(SessionLocal: Callable[[], Session]) -> Iterator[Session]:
    """چرا: مدیریت تراکنش امن و یکنواخت برای تمام ماژول‌ها"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_all_tables(engine: Engine) -> None:
    from models import Base  # lazy import to register models
    Base.metadata.create_all(bind=engine)

