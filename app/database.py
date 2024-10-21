import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Parse the DATABASE_URL from the environment variable
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

# Create the async engine for PostgreSQL
engine = create_async_engine(
    f"postgresql+asyncpg://{tmpPostgres.username}:{tmpPostgres.password}@{tmpPostgres.hostname}{tmpPostgres.path}?ssl=require",
    echo=True
)

# Create the base class for models to inherit
Base = declarative_base()

# Create the sessionmaker for async database sessions
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for getting the DB session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
