SHELL := /bin/bash

COMPOSE_FILE := infra/compose/compose.yaml
ENV_FILE := .env

.PHONY: env bootstrap compose-config compose-build compose-up compose-down compose-logs python-fmt python-lint admin-install

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

python-fmt:
	uv tool run ruff format apps/**/src

python-lint:
	uv tool run ruff check apps/**/src

admin-install:
	cd apps/admin-web && npm install

