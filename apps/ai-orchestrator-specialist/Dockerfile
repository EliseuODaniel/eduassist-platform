ARG PYTHON_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM ${PYTHON_BASE_IMAGE}

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY apps/ai-orchestrator-specialist/pyproject.toml /app/pyproject.toml
RUN uv sync --no-dev

COPY apps/ai-orchestrator-specialist/src /app/src

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["uvicorn", "ai_orchestrator_specialist.main:app", "--host", "0.0.0.0", "--port", "8000"]
