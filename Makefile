SHELL := /bin/bash

COMPOSE_FILE := infra/compose/compose.yaml
ENV_FILE := .env
SPECIALIST_PROFILE := --profile specialist-supervisor
TELEGRAM_PROFILE := --profile telegram-public
LOCAL_LLM_PROFILE := --profile local-llm-gemma4e4b
DEDICATED_CORE_SERVICES := postgres redis qdrant minio minio-init keycloak opa api-core ai-orchestrator ai-orchestrator-langgraph ai-orchestrator-python-functions ai-orchestrator-llamaindex ai-orchestrator-specialist telegram-gateway

.PHONY: env bootstrap compose-config compose-build compose-up compose-up-dedicated-core compose-up-dedicated-core-gemini-flash-lite compose-up-dedicated-core-gemma4e4b-local local-llm-gemma4e4b-down local-llm-gemma4e4b-logs compose-up-telegram-langgraph compose-up-telegram-python-functions compose-up-telegram-llamaindex compose-up-telegram-specialist compose-up-control-plane-compat compose-down compose-logs observability-up observability-down observability-logs smoke-local smoke-control-plane-compat smoke-authz smoke-adversarial smoke-all smoke-dedicated smoke-dedicated-langgraph smoke-dedicated-python-functions smoke-dedicated-llamaindex smoke-dedicated-specialist smoke-dedicated-multiturn smoke-dedicated-multiturn-langgraph smoke-dedicated-multiturn-python-functions smoke-dedicated-multiturn-llamaindex smoke-dedicated-multiturn-specialist smoke-dedicated-long-memory smoke-dedicated-long-memory-langgraph smoke-dedicated-long-memory-python-functions smoke-dedicated-long-memory-llamaindex smoke-dedicated-long-memory-specialist smoke-dedicated-semantic-ingress smoke-dedicated-semantic-ingress-langgraph smoke-dedicated-semantic-ingress-python-functions smoke-dedicated-semantic-ingress-llamaindex smoke-dedicated-semantic-ingress-specialist smoke-telegram-dedicated runtime-parity-check eval-dedicated eval-orchestrator eval-control-plane-compat eval-all graphrag-benchmark-bootstrap graphrag-benchmark-bootstrap-local graphrag-benchmark-local-check graphrag-benchmark-index graphrag-benchmark-index-dry-run graphrag-benchmark-baseline graphrag-benchmark-run graphrag-benchmark-run-smoke graphrag-local-runtime-up graphrag-local-runtime-down graphrag-local-runtime-logs release-readiness release-readiness-strict promotion-gate-check promotion-gate-check-stable article-docx db-upgrade db-downgrade db-seed-foundation db-seed-school-expansion db-seed-operational-load db-seed-deep-population db-seed-benchmark-scenarios db-seed-auth-bindings keycloak-sync-runtime-users db-bootstrap-app-role db-check-runtime-role db-check-rls backup-local backup-verify documents-sync python-fmt python-lint admin-install telegram-public-up telegram-public-up-stable telegram-webhook-info telegram-webhook-health telegram-edge-readiness

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

compose-up-dedicated-core: env
	docker compose $(SPECIALIST_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build $(DEDICATED_CORE_SERVICES)

compose-up-dedicated-core-gemini-flash-lite: env
	LLM_MODEL_PROFILE=gemini_flash_lite OPENAI_API_MODE=responses docker compose $(SPECIALIST_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build $(DEDICATED_CORE_SERVICES)

compose-up-dedicated-core-gemma4e4b-local: env
	LLM_MODEL_PROFILE=gemma4e4b_local OPENAI_API_MODE=chat_completions docker compose $(SPECIALIST_PROFILE) $(LOCAL_LLM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build $(DEDICATED_CORE_SERVICES) local-llm-gemma4e4b

local-llm-gemma4e4b-down: env
	docker compose $(LOCAL_LLM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) stop local-llm-gemma4e4b

local-llm-gemma4e4b-logs: env
	docker compose $(LOCAL_LLM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f --tail=200 local-llm-gemma4e4b

compose-up-telegram-langgraph: env
	docker rm -f eduassist-cloudflared >/dev/null 2>&1 || true
	docker compose $(SPECIALIST_PROFILE) $(TELEGRAM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) -f infra/compose/telegram-langgraph.override.yaml up -d --build $(DEDICATED_CORE_SERVICES) cloudflared
	python3 tools/ops/telegram_webhook.py register

compose-up-telegram-python-functions: env
	docker rm -f eduassist-cloudflared >/dev/null 2>&1 || true
	docker compose $(SPECIALIST_PROFILE) $(TELEGRAM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) -f infra/compose/telegram-python-functions.override.yaml up -d --build $(DEDICATED_CORE_SERVICES) cloudflared
	python3 tools/ops/telegram_webhook.py register

compose-up-telegram-llamaindex: env
	docker rm -f eduassist-cloudflared >/dev/null 2>&1 || true
	docker compose $(SPECIALIST_PROFILE) $(TELEGRAM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) -f infra/compose/telegram-llamaindex.override.yaml up -d --build $(DEDICATED_CORE_SERVICES) cloudflared
	python3 tools/ops/telegram_webhook.py register

compose-up-telegram-specialist: env
	docker rm -f eduassist-cloudflared >/dev/null 2>&1 || true
	docker compose $(SPECIALIST_PROFILE) $(TELEGRAM_PROFILE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) -f infra/compose/telegram-specialist.override.yaml up -d --build $(DEDICATED_CORE_SERVICES) cloudflared
	python3 tools/ops/telegram_webhook.py register

compose-up-control-plane-compat: env
	CONTROL_PLANE_ALLOW_DIRECT_SERVING=true docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build ai-orchestrator
	@echo "Control plane compatibility mode enabled for ai-orchestrator (/v1/messages/respond)."

compose-down: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down --remove-orphans

compose-logs: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f --tail=200

telegram-public-up: env
	docker rm -f eduassist-cloudflared >/dev/null 2>&1 || true
	docker compose --profile telegram-public --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d telegram-gateway cloudflared
	python3 tools/ops/telegram_webhook.py register

telegram-public-up-stable: env
	docker rm -f eduassist-cloudflared >/dev/null 2>&1 || true
	CLOUDFLARED_ALLOW_QUICK_TUNNEL=false docker compose --profile telegram-public --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d telegram-gateway cloudflared
	python3 tools/ops/telegram_webhook.py register

telegram-webhook-info: env
	python3 tools/ops/telegram_webhook.py info

telegram-webhook-health: env
	python3 tools/ops/telegram_webhook.py health

telegram-edge-readiness: env
	python3 tools/ops/telegram_webhook.py edge-readiness

observability-up: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d otel-collector tempo loki promtail prometheus grafana

observability-down: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) stop grafana prometheus promtail loki tempo otel-collector

observability-logs: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f --tail=200 otel-collector tempo loki promtail prometheus grafana

smoke-local: smoke-control-plane-compat

smoke-control-plane-compat: env
	@echo "Compatibility smoke for the central control plane; requires ai-orchestrator started with CONTROL_PLANE_ALLOW_DIRECT_SERVING=true."
	python3 tests/e2e/local_smoke.py

smoke-authz: env
	python3 tests/e2e/authz_regression.py

smoke-adversarial: env
	python3 tests/e2e/adversarial_regression.py

smoke-all: smoke-dedicated smoke-authz smoke-adversarial

smoke-dedicated: env
	python3 tests/e2e/dedicated_stack_smoke.py --stack $${STACK:-all}

smoke-dedicated-langgraph: env
	python3 tests/e2e/dedicated_stack_smoke.py --stack langgraph

smoke-dedicated-python-functions: env
	python3 tests/e2e/dedicated_stack_smoke.py --stack python_functions

smoke-dedicated-llamaindex: env
	python3 tests/e2e/dedicated_stack_smoke.py --stack llamaindex

smoke-dedicated-specialist: env
	python3 tests/e2e/dedicated_stack_smoke.py --stack specialist_supervisor

smoke-dedicated-multiturn: env
	python3 tests/e2e/dedicated_stack_multiturn.py --stack $${STACK:-all}

smoke-dedicated-multiturn-langgraph: env
	python3 tests/e2e/dedicated_stack_multiturn.py --stack langgraph

smoke-dedicated-multiturn-python-functions: env
	python3 tests/e2e/dedicated_stack_multiturn.py --stack python_functions

smoke-dedicated-multiturn-llamaindex: env
	python3 tests/e2e/dedicated_stack_multiturn.py --stack llamaindex

smoke-dedicated-multiturn-specialist: env
	python3 tests/e2e/dedicated_stack_multiturn.py --stack specialist_supervisor

smoke-dedicated-long-memory: env
	python3 tests/e2e/dedicated_stack_long_memory.py --stack $${STACK:-all}

smoke-dedicated-long-memory-langgraph: env
	python3 tests/e2e/dedicated_stack_long_memory.py --stack langgraph

smoke-dedicated-long-memory-python-functions: env
	python3 tests/e2e/dedicated_stack_long_memory.py --stack python_functions

smoke-dedicated-long-memory-llamaindex: env
	python3 tests/e2e/dedicated_stack_long_memory.py --stack llamaindex

smoke-dedicated-long-memory-specialist: env
	python3 tests/e2e/dedicated_stack_long_memory.py --stack specialist_supervisor

smoke-dedicated-semantic-ingress: env
	python3 tests/e2e/dedicated_stack_semantic_ingress.py --stack $${STACK:-all}

smoke-dedicated-semantic-ingress-langgraph: env
	python3 tests/e2e/dedicated_stack_semantic_ingress.py --stack langgraph

smoke-dedicated-semantic-ingress-python-functions: env
	python3 tests/e2e/dedicated_stack_semantic_ingress.py --stack python_functions

smoke-dedicated-semantic-ingress-llamaindex: env
	python3 tests/e2e/dedicated_stack_semantic_ingress.py --stack llamaindex

smoke-dedicated-semantic-ingress-specialist: env
	python3 tests/e2e/dedicated_stack_semantic_ingress.py --stack specialist_supervisor

smoke-telegram-dedicated: env
	python3 tests/e2e/telegram_gateway_dedicated_smoke.py $${TELEGRAM_GATEWAY_SMOKE_ARGS:-}

runtime-parity-check: env
	python3 tests/e2e/dedicated_runtime_parity.py --stack $${STACK:-all} $${RUNTIME_PARITY_ARGS:-}

eval-dedicated: env
	python3 tests/evals/dedicated_runtime_quality.py

eval-orchestrator: eval-control-plane-compat

eval-control-plane-compat: env
	@echo "Compatibility eval for the central control plane; requires ai-orchestrator started with CONTROL_PLANE_ALLOW_DIRECT_SERVING=true."
	python3 tests/evals/orchestrator_quality.py

eval-all: eval-dedicated

graphrag-benchmark-bootstrap: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.bootstrap_workspace --profile $${GRAPHRAG_BENCHMARK_PROFILE:-openai-remote} $${GRAPHRAG_BENCHMARK_BOOTSTRAP_ARGS:-}

graphrag-benchmark-bootstrap-local: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.bootstrap_workspace --profile local-openai-compatible --rewrite-env $${GRAPHRAG_BENCHMARK_BOOTSTRAP_ARGS:-}

graphrag-benchmark-local-check: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.local_check

graphrag-local-runtime-up: env
	bash tools/graphrag-benchmark/start_local_llamacpp_stack.sh

graphrag-local-runtime-down: env
	bash tools/graphrag-benchmark/stop_local_llamacpp_stack.sh

graphrag-local-runtime-logs: env
	docker logs --tail=120 -f $${GRAPHRAG_LOCAL_CHAT_CONTAINER:-eduassist-graphrag-chat}

graphrag-benchmark-index: env
	uv run --project tools/graphrag-benchmark graphrag index -r $${GRAPHRAG_BENCHMARK_WORKSPACE:-artifacts/graphrag/eduassist-public-benchmark} -m $${GRAPHRAG_INDEX_METHOD:-standard}

graphrag-benchmark-index-dry-run: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.dry_run_index

graphrag-benchmark-baseline: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.run_benchmark --skip-graphrag

graphrag-benchmark-run: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.run_benchmark

graphrag-benchmark-run-smoke: env
	uv run --project tools/graphrag-benchmark python -m graphrag_benchmark.run_benchmark --dataset tools/graphrag-benchmark/datasets/public_corpus_smoke.json

release-readiness: env
	.venv/bin/python tools/ops/release_readiness.py

release-readiness-strict: env
	.venv/bin/python tools/ops/release_readiness.py --strict-graphrag

promotion-gate-check: env
	.venv/bin/python tools/ops/promotion_gate.py $${PROMOTION_GATE_ARGS:-}

promotion-gate-check-stable: env
	.venv/bin/python tools/ops/promotion_gate.py --require-stable-edge $${PROMOTION_GATE_ARGS:-}

article-docx: env
	uv run --project tools/article-export python -m article_export.export_docx

db-upgrade:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core alembic -c apps/api-core/alembic.ini upgrade head

db-downgrade:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core alembic -c apps/api-core/alembic.ini downgrade -1

db-seed-foundation:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/seed_foundation.py

db-seed-school-expansion:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/seed_school_expansion.py

db-seed-operational-load:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/seed_operational_load.py

db-seed-deep-population:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/seed_deep_population.py

db-seed-benchmark-scenarios:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/seed_benchmark_scenarios.py

db-seed-auth-bindings:
	DATABASE_URL=$${DATABASE_ADMIN_URL_LOCAL:-postgresql://eduassist:eduassist@localhost:5432/eduassist} uv run --project apps/api-core python tools/mockgen/sync_auth_bindings.py

keycloak-sync-runtime-users: env
	python3 tools/mockgen/sync_keycloak_runtime_users.py

db-bootstrap-app-role: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) exec -T postgres bash /docker-entrypoint-initdb.d/02-create-app-role.sh

db-check-runtime-role:
	DATABASE_URL=$${DATABASE_APP_URL_LOCAL:-postgresql://eduassist_app:eduassist_app@localhost:5432/eduassist} uv run --project apps/api-core python tools/ops/check_db_runtime_role.py

db-check-rls:
	DATABASE_URL=$${DATABASE_APP_URL_LOCAL:-postgresql://eduassist_app:eduassist_app@localhost:5432/eduassist} uv run --project apps/api-core python tools/ops/check_db_rls.py

backup-local: env
	bash tools/ops/backup_local_stack.sh $${BACKUP_LABEL:-}

backup-verify: env
	@if [ -z "$${BACKUP_DIR:-}" ]; then echo "BACKUP_DIR is required"; exit 1; fi
	bash tools/ops/verify_local_backup.sh "$${BACKUP_DIR}"

documents-sync: env
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) exec -T worker uv run python -m worker_app.main --sync-once

python-fmt:
	uv tool run ruff format apps/**/src

python-lint:
	uv tool run ruff check apps/**/src

admin-install:
	cd apps/admin-web && npm install
