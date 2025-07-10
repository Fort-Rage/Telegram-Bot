include .env

DOCKER_EXEC = docker exec app
ALEMBIC_CMD = $(DOCKER_EXEC) alembic -c db/alembic.ini

.PHONY: new_migration upgrade upgrade_all downgrade downgrade_all history downgrade_to downgrade_to_all create_admin all downgrade_test_to

new_migration:
	$(ALEMBIC_CMD) --name=main_db revision --autogenerate -m "$(name)"

# MAIN DB
upgrade:
	$(ALEMBIC_CMD) --name=main_db upgrade head

upgrade_sql:
	$(ALEMBIC_CMD) --name=main_db upgrade head --sql > db/migrations/Plain_SQL/Full_Migration.sql

downgrade:
	$(ALEMBIC_CMD) --name=main_db downgrade -1

downgrade_to:
	$(ALEMBIC_CMD) --name=main_db downgrade "$(name)"

downgrade_to_base:
	$(ALEMBIC_CMD) --name=main_db downgrade base

# TEST DB
upgrade_test:
	$(ALEMBIC_CMD) --name=test_db upgrade head

downgrade_test:
	$(ALEMBIC_CMD) --name=test_db downgrade -1

downgrade_test_to:
	$(ALEMBIC_CMD) --name=test_db downgrade "$(name)"

version:
	$(ALEMBIC_CMD) --name=main_db current

# BOTH DBs
upgrade_all: upgrade upgrade_test

downgrade_all: downgrade downgrade_test

downgrade_to_all: downgrade_to downgrade_test_to

history:
	$(ALEMBIC_CMD) history

create_admin:
	$(DOCKER_EXEC) python db/admin_init.py

all: upgrade create_admin
