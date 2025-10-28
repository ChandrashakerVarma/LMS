<<<<<<< HEAD
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys
from dotenv import load_dotenv

# Add the root project folder to sys.path so 'app' can be imported
=======
import sys
import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# Add project root to sys.path
>>>>>>> origin/main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

<<<<<<< HEAD
# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base
from app.database import Base as DatabaseBase

# Import all models so Alembic can detect them
from app.models.organization import Organization  # must come first
from app.models import (
    role_m,
    user_m,
    course_m,
    Progress_m,        # ✅ lowercase file name
    video_m,
    QuizCheckpoint_m,  # ✅ lowercase file name
    QuizHistory_m,     # ✅ lowercase file name
    enrollment_m,
    shift_m,
    department_m,
    leavemaster_m,
    branch_m,
    category_m,
    jobposting_m,
    workflow_m,
    jobrole_m,
    candidate_m,
    candidate_document_m
)

# Target metadata for Alembic
target_metadata = DatabaseBase.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url") % {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_NAME": os.getenv("DB_NAME"),
    }
=======
# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and models
from app.database import Base  # keep only one Base import
from app.models import (
    role_m, user_m, course_m, Progress_m, video_m,
    QuizCheckpoint_m, QuizHistory_m, enrollment_m,
    shift_m, department_m, leavemaster_m,
    branch_m, category_m, organization, salary_structure_m, payroll_m, formula_m
)

# Metadata for autogenerate
target_metadata = Base.metadata

# Get DB URL
def get_database_url():
    return f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}"

# Offline migrations
def run_migrations_offline() -> None:
    url = get_database_url()
>>>>>>> origin/main
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
<<<<<<< HEAD

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    config_section = config.get_section(config.config_ini_section, {})
    config_section["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url") % {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_NAME": os.getenv("DB_NAME"),
    }

    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


=======
    with context.begin_transaction():
        context.run_migrations()

# Online migrations
def run_migrations_online() -> None:
    connectable = create_engine(get_database_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Run
>>>>>>> origin/main
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
<<<<<<< HEAD

=======
>>>>>>> origin/main
