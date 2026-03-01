"""
Database connection and session management
Supports both SQLite (dev) and PostgreSQL (production)
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Base

logger = get_logger(__name__)

# Global engine and session maker
_engine = None
_async_session_maker = None


def get_database_url() -> str:
    """
    Get database URL based on configuration
    
    Priority:
    1. DATABASE_URL environment variable (PostgreSQL)
    2. SQLite (default for development)
    """
    # Check if PostgreSQL URL is configured
    import os
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Convert PostgreSQL URL to async format if needed
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return database_url
    
    # Default to SQLite for development
    return "sqlite+aiosqlite:///./patentai.db"


def init_db():
    """Initialize database engine and session maker"""
    global _engine, _async_session_maker
    
    database_url = get_database_url()
    logger.info("Initializing database", url=database_url.split("://")[0] + "://***")
    
    # Engine configuration
    engine_kwargs = {
        "echo": settings.debug,  # Log SQL queries in debug mode
    }
    
    # SQLite-specific configuration
    if "sqlite" in database_url:
        engine_kwargs.update({
            "poolclass": NullPool,  # Disable connection pooling for SQLite
            "connect_args": {
                "check_same_thread": False,
            }
        })
    
    _engine = create_async_engine(database_url, **engine_kwargs)
    _async_session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    logger.info("Database engine initialized")


async def close_db():
    """Close database connections"""
    global _engine
    
    if _engine:
        await _engine.dispose()
        logger.info("Database connections closed")


async def create_tables():
    """Create all database tables"""
    global _engine
    
    if not _engine:
        init_db()
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")


async def drop_tables():
    """Drop all database tables (use with caution!)"""
    global _engine
    
    if not _engine:
        init_db()
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.info("Database tables dropped")


from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session
    
    Usage:
        async with get_db() as db:
            result = await db.execute(...)
    """
    global _async_session_maker
    
    if not _async_session_maker:
        init_db()
    
    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Simpler alternative for FastAPI dependency injection
async def get_db_session() -> AsyncSession:
    """Get database session (for FastAPI Depends)"""
    global _async_session_maker
    
    if not _async_session_maker:
        init_db()
    
    async with _async_session_maker() as session:
        yield session


class DatabaseManager:
    """
    High-level database operations
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # Library operations
    async def create_library(self, library_data: dict) -> dict:
        """Create a new patent library"""
        from app.db.models import LibraryModel
        
        library = LibraryModel(**library_data)
        self.session.add(library)
        await self.session.commit()
        await self.session.refresh(library)
        
        logger.info("Library created", library_id=library.id)
        return library.to_dict()
    
    async def get_library(self, library_id: str) -> Optional[dict]:
        """Get library by ID"""
        from app.db.models import LibraryModel
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(LibraryModel).where(LibraryModel.id == library_id)
        )
        library = result.scalar_one_or_none()
        
        return library.to_dict() if library else None
    
    async def list_libraries(self) -> list:
        """List all libraries"""
        from app.db.models import LibraryModel
        from sqlalchemy import select
        
        result = await self.session.execute(select(LibraryModel))
        libraries = result.scalars().all()
        
        return [lib.to_dict() for lib in libraries]
    
    async def delete_library(self, library_id: str) -> bool:
        """Delete library and all its patents"""
        from app.db.models import LibraryModel
        from sqlalchemy import delete
        
        result = await self.session.execute(
            delete(LibraryModel).where(LibraryModel.id == library_id)
        )
        await self.session.commit()
        
        return result.rowcount > 0
    
    # Patent operations
    async def create_patent(self, patent_data: dict) -> dict:
        """Create a new patent"""
        from app.db.models import PatentModel
        
        patent = PatentModel(**patent_data)
        self.session.add(patent)
        await self.session.commit()
        await self.session.refresh(patent)
        
        # Update library patent count
        await self._update_library_count(patent.library_id)
        
        logger.info("Patent created", patent_id=patent.id, library_id=patent.library_id)
        return patent.to_dict()
    
    async def get_patent(self, patent_id: str, include_embedding: bool = False) -> Optional[dict]:
        """Get patent by ID"""
        from app.db.models import PatentModel
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(PatentModel).where(PatentModel.id == patent_id)
        )
        patent = result.scalar_one_or_none()
        
        return patent.to_dict(include_embedding=include_embedding) if patent else None
    
    async def list_patents(self, library_id: Optional[str] = None) -> list:
        """List patents, optionally filtered by library"""
        from app.db.models import PatentModel
        from sqlalchemy import select
        
        query = select(PatentModel)
        if library_id:
            query = query.where(PatentModel.library_id == library_id)
        
        result = await self.session.execute(query)
        patents = result.scalars().all()
        
        return [p.to_dict() for p in patents]
    
    async def update_patent_embedding(self, patent_id: str, embedding: list, dimensions: int):
        """Update patent embedding"""
        from app.db.models import PatentModel
        from sqlalchemy import update
        
        await self.session.execute(
            update(PatentModel)
            .where(PatentModel.id == patent_id)
            .values(
                embedding=embedding,
                embedding_dimensions=dimensions,
                updated_at=datetime.utcnow()
            )
        )
        await self.session.commit()
        
        logger.info("Patent embedding updated", patent_id=patent_id)
    
    async def _update_library_count(self, library_id: str):
        """Update library patent count"""
        from app.db.models import LibraryModel, PatentModel
        from sqlalchemy import select, func, update
        
        # Count patents in library
        result = await self.session.execute(
            select(func.count()).where(PatentModel.library_id == library_id)
        )
        count = result.scalar()
        
        # Update library
        await self.session.execute(
            update(LibraryModel)
            .where(LibraryModel.id == library_id)
            .values(patent_count=count, updated_at=datetime.utcnow())
        )
        await self.session.commit()
    
    # Task operations
    async def create_task(self, task_data: dict) -> dict:
        """Create a new analysis task"""
        from app.db.models import TaskModel
        
        task = TaskModel(**task_data)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        
        logger.info("Task created", task_id=task.id)
        return task.to_dict()
    
    async def get_task(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        from app.db.models import TaskModel
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        return task.to_dict() if task else None
    
    async def update_task(self, task_id: str, updates: dict) -> bool:
        """Update task fields"""
        from app.db.models import TaskModel
        from sqlalchemy import update
        
        result = await self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == task_id)
            .values(**updates, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        
        return result.rowcount > 0


# Import datetime for DatabaseManager
from datetime import datetime
