from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from rotoger import Rotoger
from config import settings as global_settings
from collections.abc import AsyncGenerator
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import ResponseValidationError

logger = Rotoger().get_logger()

engine = create_async_engine(
    global_settings.asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=True,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            raise
        except Exception as ex:
            # Only log actual database-related issues, not response validation
            if not isinstance(ex, ResponseValidationError):
                await logger.aerror(f"Database-related error: {repr(ex)}")
            raise  # Re-raise to be handled by appropriate handlers
