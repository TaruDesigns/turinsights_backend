from contextlib import contextmanager
from typing import Any, Generator, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator:
    """Gets DB Session as a contextmanager

    Yields:
        Generator: db session
    """
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_depends() -> Generator:
    """Gets DB Session as a regular generator, for FastAPI Depends()

    Yields:
        Generator: db session
    """
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()
