from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.database import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# This is the Alembic Config object, which provides access to the .ini file values.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set up the metadata object for 'autogenerate' support.
target_metadata = Base.metadata

# Load the database URL and replace the async driver with a sync driver for Alembic migrations
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql+asyncpg", "postgresql+psycopg2")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create a synchronous engine to be used by Alembic
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
