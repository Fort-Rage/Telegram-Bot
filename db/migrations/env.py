import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from db.database import DATABASE_URL, TEST_DATABASE_URL
from db.models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


db_name = None
for arg in sys.argv:
    if arg.startswith("--name="):
        db_name = arg.split("=")[1]

if db_name == "main_db":
    db_url = DATABASE_URL
elif db_name == "test_db":
    db_url = TEST_DATABASE_URL
else:
    raise ValueError(f"Unknown database section: {db_name}")

config.set_section_option("main_db", "sqlalchemy.url", DATABASE_URL)
config.set_section_option("test_db", "sqlalchemy.url", TEST_DATABASE_URL)


def run_migrations_offline() -> None:
    def do_offline_migration(url):
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    do_offline_migration(db_url)


def run_migrations_online() -> None:
    def do_online_migration(url):
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            poolclass=pool.NullPool,
            url=url
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()

    do_online_migration(db_url)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
