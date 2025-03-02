from sqlalchemy import create_engine
from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Προσθήκη του path του project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from backend.models import Base
target_metadata = Base.metadata

# Χρήση του DATABASE_URL από το .env
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.getenv('DATABASE_URL')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Χρησιμοποίηση του DATABASE_URL απευθείας
    url = os.getenv('DATABASE_URL')
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:

    run_migrations_online()
