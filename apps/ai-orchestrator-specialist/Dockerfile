ARG PYTHON_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /workspace/apps/ai-orchestrator-specialist

COPY packages/observability/python /workspace/packages/observability/python
COPY packages/semantic-ingress/python /workspace/packages/semantic-ingress/python
COPY apps/ai-orchestrator-specialist/pyproject.toml ./
COPY apps/ai-orchestrator-specialist/uv.lock ./
COPY apps/ai-orchestrator-specialist/src ./src

RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "ai_orchestrator_specialist.main:app", "--host", "0.0.0.0", "--port", "8000"]
