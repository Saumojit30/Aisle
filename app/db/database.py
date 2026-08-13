import logging
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# Create Async Engine
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

async_engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args=connect_args,
)

async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        logger.info("Initializing database tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database initialization complete.")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes to get a database session."""
    async with async_session_maker() as session:
        yield session
