SHELL := /bin/bash

COMPOSE_FILE := infra/compose/compose.yaml
ENV_FILE := .env

.PHONY: env bootstrap compose-config compose-build compose-up compose-down compose-logs observability-up observability-down observability-logs smoke-local smoke-authz smoke-adversarial smoke-all db-upgrade db-downgrade db-seed-foundation db-seed-auth-bindings db-bootstrap-app-role db-check-runtime-role documents-sync python-fmt python-lint admin-install

env:
	@if [ ! -f $(ENV_FILE) ]; then cp .env.example $(ENV_FILE); fi

bootstrap: env
	@echo "Environment file ready at $(ENV_FILE)"

compose-config: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) config >/dev/null
	@echo "Compose configuration is valid."

compose-build: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) build

compose-up: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build

compose-down: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down --remove-orphans

compose-logs: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f --tail=200

observability-up: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d otel-collector tempo loki promtail prometheus grafana

observability-down: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) stop grafana prometheus promtail loki tempo otel-collector

observability-logs: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f --tail=200 otel-collector tempo loki promtail prometheus grafana

smoke-local: env
	python3 tests/e2e/local_smoke.py

smoke-authz: env
	python3 tests/e2e/authz_regression.py

smoke-adversarial: env
	python3 tests/e2e/adversarial_regression.py

smoke-all: smoke-local smoke-authz smoke-adversarial

db-upgrade:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core alembic -c apps/api-core/alembic.ini upgrade head

db-downgrade:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core alembic -c apps/api-core/alembic.ini downgrade -1

db-seed-foundation:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/seed_foundation.py

db-seed-auth-bindings:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/sync_auth_bindings.py

db-bootstrap-app-role: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) exec -T postgres bash /docker-entrypoint-initdb.d/02-create-app-role.sh

db-check-runtime-role:
	DATABASE_URL=$${DATABASE_APP_URL_LOCAL:-postgresql://eduassist_app:eduassist_app@localhost:5432/eduassist} uv run --project apps/api-core python tools/ops/check_db_runtime_role.py

documents-sync: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) exec -T worker uv run python -m worker_app.main --sync-once

python-fmt:
	uv tool run ruff format apps/**/src

python-lint:
	uv tool run ruff check apps/**/src

admin-install:
	cd apps/admin-web && npm install
