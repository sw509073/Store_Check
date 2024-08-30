from __future__ import annotations
import logging
from logging.config import fileConfig
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from alembic import context

# Import your application's SQLAlchemy object
from app import create_app, db

# Set up logging
config = context.config
fileConfig(config.config_file_name, disable_existing_loggers=False)
logger = logging.getLogger('alembic.runtime.migration')

def run_migrations_online() -> None:
    connectable = db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=db.metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()

def include_object(object, name, type_, reflected, compare_to):
    # Include only tables and ignore other types of objects
    return type_ in ('table',)

def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=db.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
