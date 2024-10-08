import asyncio
from collections import deque
from contextlib import AbstractContextManager, asynccontextmanager, contextmanager
from typing import Generator

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# We have two different engines because one is sync while the other is async.
# The async engine uses a special connection pool with round robin assignment to avoid creating multiple sessions that would degrade performance
# or run the risk of hitting max connections. The default pool DOES NOT avoid this limit issue or has concurrency errors.

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)  # type: ignore
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# poolclass NullPool is CRITICAL to avoid really weird asyncio errors that can't be debugged
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI_ASYNC, pool_pre_ping=True, echo=False, poolclass=NullPool
)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


class DBContext(AbstractContextManager):
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.db.rollback()
            self.db.close()
            # Return True to suppress any exceptions
            return True
        self.db.close()
        # Return False to propagate exceptions
        return False


class ConnectionPool:
    # Async connection pool with round robin assignment using asyncpg.
    def __init__(self, pool_size: int):
        self.pool_size = pool_size
        self.lock = asyncio.Lock()  # Ensure async-safe access
        self.sessions = deque(maxlen=pool_size)  # Pool to store sessions
        self.current = 0  # Current round-robin index
        self.initialize_pool()  # This is SYNC to make sure it actually gets initialized without any asyncio gather issues

    def initialize_pool(self):
        """Initialize all the DB sessions in the pool"""
        # Create async engine and session factory
        self.engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI_ASYNC,
            echo=False,
            poolclass=NullPool,
        )
        self.async_session_factory = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

        # Prepopulate the pool with sessions
        for _ in range(self.pool_size):
            session = self.async_session_factory()
            self.sessions.append(session)

    async def get_async_dbsession(self):
        """Returns a DB session in a round-robin manner"""
        async with self.lock:  # Ensure that session allocation is async-safe
            session = self.sessions[self.current]
            self.current = (self.current + 1) % self.pool_size
            return session

    async def close_all_sessions(self):
        """Close all DB sessions"""
        for session in self.sessions:
            await session.close()

    async def dispose_engine(self):
        """Dispose of the engine (when shutting down the app)"""
        await self.engine.dispose()


# Create a connection pool object
db_pool = ConnectionPool(pool_size=settings.MAX_DB_CONNECTIONS)


@asynccontextmanager
async def get_db_async_pool():
    """Gets DB Session as an async context manager from the pool."""
    session = await db_pool.get_async_dbsession()  # Get session from the pool
    try:
        yield session  # Provide the session to the caller
        # await session.commit()  # Commit after successful operation
    except Exception as e:
        # await session.rollback()  # Rollback if there is an error
        # raise  # Re-raise the exception after rollback
        pass


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
    """Gets DB Session as an async context manager. Creates a new session each time."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Ensure commit is awaited
        except Exception as e:
            await session.rollback()  # Rollback in case of exception
            raise
        finally:
            await session.close()
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
        db.close()
