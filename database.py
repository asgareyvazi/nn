# File: database.py
# Purpose: SQLAlchemy engine/session factory wrapper with context manager get_session()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import Base

class Database:
    def __init__(self, db_path="nikan.db", echo=False):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=echo)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        s = self.Session()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()
