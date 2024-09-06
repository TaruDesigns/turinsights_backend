from contextlib import asynccontextmanager, contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)  # type: ignore
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI_ASYNC,
    pool_pre_ping=True,
    echo=False,
)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


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


@asynccontextmanager
async def get_db_async():
    """Gets DB Session as an async context manager."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Ensure commit is awaited
        except Exception as e:
            await session.rollback()  # Rollback in case of exception
            raise
        finally:
            # No need to explicitly close, it's managed by async context
            pass


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
