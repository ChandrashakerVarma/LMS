import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
from dotenv import load_dotenv

# --- Add project root to sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Load environment variables ---
load_dotenv()

# --- Import Base metadata and DATABASE_URL from your database config ---
from app.database import Base, DATABASE_URL
# Ensure all models are imported for Alembic autogenerate
from app.models import organization, course_m, role_m, user_m, Progress_m, video_m, QuizCheckpoint_m, QuizHistory_m, enrollment_m, branch_m

# Alembic Config object
config = context.config

# Always use DATABASE_URL from .env, ignore alembic.ini url
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # detect column type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # detect column type changes
        )

        with context.begin_transaction():
            context.run_migrations()


# Run migrations depending on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
